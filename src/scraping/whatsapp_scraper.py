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

cursor.execute("""
CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remitente TEXT,
    contenido TEXT,
    fecha_hora TEXT
)
""")
conn.commit()
# -------------------------
# Inicializar navegador
# -------------------------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument(r"--user-data-dir=C:\Users\Josue\Documents\Whatsapp-Empleo-Bot\chrome_cache")
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
# Extraer mensajes
# -------------------------
mensajes = driver.find_elements(
    By.XPATH,
    "//span[contains(@class,'selectable-text') or @data-testid='message-text']"
)

print(f"📩 Se encontraron {len(mensajes)} mensajes visibles.\n")

for m in mensajes:
    try:
        texto = m.text.strip()
        if texto:
            cursor.execute(
                "INSERT INTO mensajes (remitente, contenido) VALUES (?, ?)",
                (nombre_canal, texto))
            
            print(f"💬 Guardado en BD: {texto}")
    except Exception as e:
        print(f"⚠️ Error al insertar: {e}")

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


