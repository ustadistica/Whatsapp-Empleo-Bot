import os
import time
import sqlite3
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configuración
NOMBRE_CANAL = "Empleo en Bogotá"
WAIT_TIMEOUT = 20
DB_PATH = "whatsapp_mensajes.db"
CSV_PATH = "whatsapp_mensajes.csv"

# Conectar a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canal TEXT,
    texto TEXT
)
''')
conn.commit()

# Agregar columna fecha si no existe
try:
    cursor.execute("ALTER TABLE mensajes ADD COLUMN fecha TEXT")
    conn.commit()
except sqlite3.OperationalError:
    # La columna ya existe
    pass

def guardar_mensaje_db(fecha, canal, texto):
    cursor.execute(
        "INSERT INTO mensajes (fecha, canal, texto) VALUES (?, ?, ?)",
        (fecha, canal, texto)
    )
    conn.commit()

def guardar_mensajes_csv(mensajes):
    df = pd.DataFrame(mensajes, columns=["fecha", "canal", "texto"])
    if os.path.exists(CSV_PATH):
        df.to_csv(CSV_PATH, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"💾 Mensajes guardados en CSV: {CSV_PATH}")

def iniciar_driver():
    options = Options()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def abrir_whatsapp(driver):
    driver.get("https://web.whatsapp.com")
    print("📲 Abriendo WhatsApp Web. Escanea el QR si no estás logueado...")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "app"))
    )
    time.sleep(2)

def ir_a_pestania_canales(driver):
    try:
        canales_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(@aria-label,'Canales') or contains(@aria-label,'Channels')]")
            )
        )
        canales_btn.click()
        print("✅ Pestaña de canales abierta")
        time.sleep(3)
    except Exception as e:
        print(f"⚠️ No se pudo abrir la pestaña de canales: {e}")

def buscar_y_abrir_canal(driver, nombre_canal):
    try:
        buscador = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
        )
        buscador.click()
        buscador.send_keys(Keys.CONTROL + "a")
        buscador.send_keys(Keys.DELETE)
        buscador.send_keys(nombre_canal)
        time.sleep(2)
        canal_element = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, f'//span[@title="{nombre_canal}"]'))
        )
        canal_element.click()
        print(f"✅ Canal '{nombre_canal}' abierto")
        time.sleep(3)
    except Exception as e:
        print(f"❌ No se encontró el canal '{nombre_canal}'. Error: {e}")
        driver.quit()
        exit()

def extraer_mensajes(driver, canal, n=30):
    mensajes = driver.find_elements(
        By.XPATH,
        "//span[contains(@class,'selectable-text') or @data-testid='message-text']"
    )
    print(f"📩 Encontrados {len(mensajes)} mensajes visibles en '{canal}'\n")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensajes_guardados = []
    cont = 0
    for m in mensajes[-n:]:
        texto = m.text.strip()
        if texto:
            guardar_mensaje_db(fecha, canal, texto)
            mensajes_guardados.append([fecha, canal, texto])
            print(f"💬 Guardado: {texto}")
            cont += 1
    guardar_mensajes_csv(mensajes_guardados)
    print(f"💾 Mensajes guardados en la base de datos y CSV: {cont}")

def main():
    driver = iniciar_driver()
    try:
        abrir_whatsapp(driver)
        ir_a_pestania_canales(driver)
        buscar_y_abrir_canal(driver, NOMBRE_CANAL)
        extraer_mensajes(driver, NOMBRE_CANAL)
        input("Presiona Enter para cerrar el navegador...")
    finally:
        driver.quit()
        conn.close()
        print("🏁 Script finalizado.")

if __name__ == "__main__":
    main()
