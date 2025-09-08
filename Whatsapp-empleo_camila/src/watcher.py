
import os, asyncio
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from db import insert_oferta, export_csv
from parser import parse_message
from push import git_push

load_dotenv()

CHANNEL_URL = os.getenv("CHANNEL_URL")
REPO_PATH   = os.getenv("REPO_PATH")  # opcional; si está vacío, se autodetecta
PROFILE_DIR = Path.home() / ".whatsapp-jobs"  # sesión persistente de WhatsApp
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Selectores en cascada para tolerar cambios de UI
SELECTORS_CANDIDATOS = [
    "div.message-in, div.message-out",              # chats
    "div[role='article']",                          # posts de canal como artículos
    "div._amk9",                                    # contenedor genérico (clases ofuscadas)
    "div[data-id] div.selectable-text",             # spans de texto
]

MSG_TEXT_SELECTORS = [
    "div.selectable-text span",
    "span[dir='auto']",
    "div[role='textbox'] span",
]

JOB_HINTS = (
    "vacante", "oferta", "convocatoria", "se requiere", "se necesita",
    "analista", "cient", "data", "ingenier", "developer", "practic", "intern",
    "salario", "hv", "hoja de vida", "enviar cv", "postúlate", "postulate"
)

def parece_oferta(txt: str) -> bool:
    t = txt.lower()
    return any(h in t for h in JOB_HINTS)

async def open_target(page, channel_url: str | None):
    if channel_url:
        await page.goto(channel_url)
        await page.wait_for_selector("main", timeout=0)
    else:
        await page.goto("https://web.whatsapp.com/")
        await page.wait_for_selector("main", timeout=0)

async def get_recent_text_blocks(page, limit=40):
    texts = []
    for cont_sel in SELECTORS_CANDIDATOS:
        containers = page.locator(cont_sel)
        count = await containers.count()
        if count == 0:
            continue
        for i in range(max(0, count - limit), count):
            cont = containers.nth(i)
            inner_texts = []
            for ts in MSG_TEXT_SELECTORS:
                try:
                    tnodes = await cont.locator(ts).all_inner_texts()
                    inner_texts.extend(tnodes)
                except:
                    pass
            if not inner_texts:
                try:
                    txt = await cont.inner_text()
                    if txt:
                        inner_texts.append(txt)
                except:
                    pass
            if inner_texts:
                texts.append("\n".join([t for t in inner_texts if t and t.strip()]))
    seen = set(); cleaned = []
    for t in texts:
        k = t.strip()
        if k and k not in seen:
            cleaned.append(k); seen.add(k)
    return cleaned[-limit:]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False
        )
        page = await browser.new_page()
        await page.goto("https://web.whatsapp.com/")
        try:
            # Espera a que desaparezca el QR (sesión iniciada)
            await page.wait_for_selector("canvas[aria-label='Scan me!']", state="detached", timeout=0)
        except:
            pass

        await open_target(page, CHANNEL_URL)

        print("[INFO] Monitoreando canal:", CHANNEL_URL or "(WhatsApp Web)")

        seen_hashes = set()
        while True:
            try:
                msgs = await get_recent_text_blocks(page, limit=40)
                for m in msgs:
                    if not parece_oferta(m):
                        continue
                    row = parse_message(m, CHANNEL_URL or "Canal", datetime.now())
                    if row["id"] in seen_hashes:
                        continue
                    if insert_oferta(row):
                        print("➕ Nueva oferta:", row["titulo"] or "(sin título)")
                        seen_hashes.add(row["id"])
                        export_csv()
                        git_push(REPO_PATH, f"chore(data): oferta {row['id'][:7]} {row['titulo'] or ''}")
                await page.wait_for_timeout(5000)  # 5s
            except Exception as e:
                print("[ERROR ciclo]:", e)
                await page.wait_for_timeout(5000)

if __name__ == "__main__":
    asyncio.run(run())
