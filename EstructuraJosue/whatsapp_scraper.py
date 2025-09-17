from datetime import datetime
import time
import sqlite3
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------
# Configuración
# -------------------------
nombre_canal = "Empleo en Bogotá"
db_path = "whatsapp.db"   # Ruta de la base de datos SQLite
wait_timeout = 15

# -------------------------
# Función para validar texto (descartar emojis sueltos)
# -------------------------
def es_texto_valido(texto):
    return bool(re.search(r"[A-Za-zÁÉÍÓÚáéíóúñÑ0-9]", texto))

# -------------------------
# Conectar a la base de datos
# -------------------------
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# -------------------------
# Inicializar navegador
# -------------------------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# -------------------------
# Abrir WhatsApp Web
# -------------------------
driver.get("https://web.whatsapp.com")
print("📲 Abriendo WhatsApp Web. Escanea el QR si no estás logueado...")

WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, "//div[@id='app']"))
)

time.sleep(20)

# -------------------------
# Ir a la pestaña de canales
# -------------------------
try:
    canales_btn = WebDriverWait(driver, wait_timeout).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(@aria-label,'Canales') or contains(@aria-label,'Channels')]"))
    )
    canales_btn.click()
    print("✅ Pestaña de canales abierta")
    time.sleep(2)
except Exception as e:
    print(f"⚠️ No se pudo abrir la pestaña de canales: {e}")

# -------------------------
# Buscar canal
# -------------------------
try:
    buscador = WebDriverWait(driver, wait_timeout).until(
        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
    )
    buscador.click()
    buscador.send_keys(Keys.CONTROL + "a")
    buscador.send_keys(Keys.DELETE)
    buscador.send_keys(nombre_canal)
    time.sleep(2)

    canal = driver.find_element(By.XPATH, f'//span[@title="{nombre_canal}"]')
    canal.click()
    print(f"✅ Canal '{nombre_canal}' abierto correctamente")
except Exception as e:
    print(f"❌ No se encontró el canal '{nombre_canal}'. Error: {e}")
    driver.quit()
    exit()

time.sleep(3)

# -------------------------
# Hacer scroll en el chat para cargar más mensajes
# -------------------------
mensajes_guardados = set()

try:
    posibles_selectores = [
        "//div[@aria-label='Mensajes']",
        "//div[@aria-label='Messages']",
        "//div[@role='region']",
        "//div[contains(@class,'x1n2onr6')]",
        "//div[contains(@class,'_ak9t')]"
    ]
    
    chat_box = None
    for selector in posibles_selectores:
        try:
            chat_box = WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            print(f"✅ Contenedor encontrado con selector: {selector}")
            break
        except:
            continue

    if not chat_box:
        raise Exception("No se pudo localizar el contenedor del chat.")

    # Scroll en bucle
    for i in range(5):  # Ajusta cuántos ciclos de scroll quieres
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop - 800;", chat_box)
        time.sleep(2)

        # Buscar mensajes de texto y mensajes en imágenes con alt
        mensajes_texto = driver.find_elements(
            By.XPATH,
            "//span[contains(@class,'selectable-text') or @data-testid='message-text']"
        )
        mensajes_img = driver.find_elements(By.XPATH, "//img[@alt]")
        mensajes = mensajes_texto + mensajes_img

        print(f"📩 Ciclo {i+1}: {len(mensajes)} mensajes visibles")

        for m in mensajes:
            try:
                # Extraer texto
                if m.tag_name == "img":
                    texto = m.get_attribute("alt").strip()
                else:
                    texto = m.text.strip()

                # Extraer fecha/hora desde el atributo title (ejemplo: "16/9/2025 21:56")
                fecha_hora = m.get_attribute("title")
                if fecha_hora:
                    try:
                        # Ajustar formato según cómo WhatsApp muestre la fecha en tu idioma
                        fecha_dt = datetime.strptime(fecha_hora, "%d/%m/%Y %H:%M")
                        fecha_str = fecha_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Guardar solo si es texto válido y no está repetido
                if texto and es_texto_valido(texto) and (texto, fecha_str) not in mensajes_guardados:
                    mensajes_guardados.add((texto, fecha_str))
                    cursor.execute(
                        "INSERT INTO mensajes (remitente, contenido, fecha_hora) VALUES (?, ?, ?)",
                        (nombre_canal, texto, fecha_str)
                    )
                    print(f"💬 Guardado en BD: {texto} | 🕒 {fecha_str}")

            except Exception as e:
                print(f"⚠️ Error al insertar mensaje: {e}")

except Exception as e:
    print(f"⚠️ No se pudo hacer scroll o extraer mensajes: {e}")

# -------------------------
# Guardar en BD
# -------------------------
conn.commit()
print("💾 Mensajes guardados en la base de datos.")

# -------------------------
# Fin
# -------------------------
conn.close()
print("🏁 Script terminado. El navegador queda abierto para inspección manual.")


