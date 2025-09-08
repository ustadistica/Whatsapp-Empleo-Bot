import os, time
from datetime import datetime

# ====== Config ======
from dotenv import load_dotenv
load_dotenv()

TARGET = os.getenv("WHATSAPP_TARGET", "Ofertas")
TARGET_TYPE = os.getenv("TARGET_TYPE", "channel").strip().lower()  # "channel" o "chat"

DATA_PATH = os.getenv("DATA_PATH", "C:/CamiBot/data/ofertas.csv")
CSV_SEP = os.getenv("CSV_SEP", "|")
# ignoramos el encoding del .env y usamos siempre utf-8-sig
CSV_ENCODING = "utf-8-sig"

QR_WAIT = int(os.getenv("QR_WAIT_SECONDS", "25"))
N_MENSAJES = int(os.getenv("N_MENSAJES", "30"))

# ====== Dependencias ======
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# ====== Utilidades de archivo ======
def asegurar_directorios():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

def leer_base():
    if os.path.exists(DATA_PATH):
        try:
            return pd.read_csv(DATA_PATH, sep=CSV_SEP, encoding=CSV_ENCODING)
        except Exception:
            pass
    return pd.DataFrame(columns=["fecha", "texto", "fuente"])

def guardar(ofertas_nuevas):
    base = leer_base()
    nuevo = pd.DataFrame(ofertas_nuevas)
    df = pd.concat([base, nuevo], ignore_index=True).drop_duplicates(subset=["texto"]).reset_index(drop=True)

    # Guardar en CSV
    df.to_csv(DATA_PATH, index=False, sep=CSV_SEP, encoding=CSV_ENCODING)

    # Guardar también en Excel (mismo nombre, diferente extensión)
    try:
        xlsx_path = DATA_PATH.replace(".csv", ".xlsx")
        df.to_excel(xlsx_path, index=False)
        print(f"📄 Excel también guardado en: {xlsx_path}")
    except Exception as e:
        print("No se pudo crear el Excel:", e)

    return len(df) - len(base)


# ====== Navegación WhatsApp ======
def iniciar_driver():
    opts = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.maximize_window()
    return driver

def abrir_whatsapp(driver):
    driver.get("https://web.whatsapp.com")
    print("Escanea el QR con tu celular…")
    time.sleep(QR_WAIT)

def ir_a_updates(driver):
    candidatos = [
        "//div[@role='tab' and (@aria-label='Novedades' or @aria-label='Updates')]",
        "//span[normalize-space()='Novedades']/ancestor::div[@role='tab']",
        "//span[normalize-space()='Updates']/ancestor::div[@role='tab']",
        "//div[@data-testid='updates-tab']",
    ]
    for xp in candidatos:
        try:
            el = driver.find_element(By.XPATH, xp)
            el.click()
            time.sleep(1.5)
            return
        except NoSuchElementException:
            continue

def encontrar_caja_busqueda_chats(driver):
    candidatos = [
        "//div[@contenteditable='true' and @data-tab='3']",
        "//div[@contenteditable='true' and @data-tab='2']",
        "//div[@role='textbox' and @title='Buscar o empezar un chat']",
        "//div[@role='textbox' and @aria-label='Search or start new chat']",
    ]
    for xp in candidatos:
        try:
            return driver.find_element(By.XPATH, xp)
        except NoSuchElementException:
            continue
    return None

def abrir_objetivo(driver, nombre, tipo="channel"):
    if tipo == "chat":
        caja = encontrar_caja_busqueda_chats(driver)
        if caja:
            caja.click()
            try: caja.clear()
            except: pass
            caja.send_keys(nombre)
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, f"//span[@title='{nombre}']").click()
                time.sleep(1.5)
                return
            except NoSuchElementException:
                pass
        print(f"No se pudo buscar el chat '{nombre}'. Ábrelo manualmente y presiona Enter…")
        input()
        return

    # tipo == "channel"
    ir_a_updates(driver)
    time.sleep(1.0)
    try:
        driver.find_element(By.XPATH, f"//span[@title='{nombre}']").click()
        time.sleep(2)
        return
    except NoSuchElementException:
        try:
            driver.find_element(By.XPATH, f"//div[@aria-label='{nombre}']").click()
            time.sleep(2)
            return
        except NoSuchElementException:
            print(f"No se encontró el canal '{nombre}'. Ábrelo manualmente y presiona Enter…")
            input()

def extraer_textos_generico(driver, n=30):
    selectores_mensaje = [
        "//div[contains(@class,'message-in') or contains(@class,'message-out')]",
        "//div[@data-testid='msg-container']",
        "//div[@role='row']"
    ]
    elementos = []
    for xp in selectores_mensaje:
        try:
            elementos = driver.find_elements(By.XPATH, xp)
            if elementos:
                break
        except Exception:
            continue

    if not elementos:
        return []

    if len(elementos) > n:
        elementos = elementos[-n:]

    textos = []
    selectores_texto = [
        ".//span[@class='selectable-text copyable-text']",
        ".//div[contains(@class,'_ao3e') or contains(@class,'_am-g')]//span",
        ".//div[contains(@data-pre-plain-text,'[')]//span[@class='selectable-text copyable-text']",
        ".//span[@dir='ltr' or @dir='auto']",
    ]
    for m in elementos:
        txt = None
        for xp in selectores_texto:
            try:
                t = m.find_element(By.XPATH, xp).text.strip()
                if t:
                    txt = t
                    break
            except Exception:
                continue
        if txt:
            textos.append(txt)
    return textos

def normalizar(lista_texto, fuente):
    hoy = datetime.now().strftime("%Y-%m-%d")
    return [{"fecha": hoy, "texto": t, "fuente": fuente} for t in lista_texto]

def main():
    asegurar_directorios()
    driver = iniciar_driver()
    try:
        abrir_whatsapp(driver)
        abrir_objetivo(driver, TARGET, tipo=TARGET_TYPE)
        textos = extraer_textos_generico(driver, n=N_MENSAJES)
        ofertas = normalizar(textos, fuente=TARGET)
        agregados = guardar(ofertas)
        print(f"✅ Ofertas agregadas (sin duplicados): {agregados}")
        print(f"📂 Archivo: {DATA_PATH}")
        input("Presiona Enter para cerrar…")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

