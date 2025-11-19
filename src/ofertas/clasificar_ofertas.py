import os
import json
import re
from pathlib import Path

import pandas as pd
from google import genai
from dotenv import load_dotenv

# === Cargar .env desde la carpeta del proyecto ===

SCRIPT_DIR = Path(__file__).resolve().parent  # carpeta Proyecto_Ofertas_Empleo
DOTENV_PATH = SCRIPT_DIR / ".env"

load_dotenv(dotenv_path=DOTENV_PATH)
print(f"[DEBUG] Usando .env en: {DOTENV_PATH}")

# ============= CONFIG =============
RUTA_JSON_ENTRADA = SCRIPT_DIR / "analisis_ofertas_empleo.json"
RUTA_JSON_SALIDA = SCRIPT_DIR / "analisis_ofertas_empleo_clasificado.json"

# Ruta de la tabla CUOC (ajusta si está en otro sitio o nombre)
CUOC_INDEX_PATH = SCRIPT_DIR / "CUOC-indice-2024.xlsx"
MAX_FILAS_CUOC = 200          # para no meter toda la tabla en el prompt
MAX_LLM_CALLS = 4             # SOLO 1 llamada a Gemini (modo prueba)

# Modelo de Gemini
GEMINI_MODEL = "gemini-2.5-flash"

# Categorías que vamos a usar
CATEGORIES = [
    "Call center/BPO",
    "Logística/Bodega",
    "Salud",
    "Retail/Comercial",
    "Tecnología/Ingeniería",
    "Administrativo/Facturación",
    "Conducción/Operaciones",
    "Evento/Curso (no empleo)",
    "Sin clasificar",  # la dejamos explícita
]

# ============= CLIENTE GEMINI =============

def get_client():
    """
    Crea el cliente de Gemini.
    Usa la variable GEMINI_API_KEY o GOOGLE_API_KEY del .env.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY / GOOGLE_API_KEY. "
            "Defínela en tu archivo .env dentro de Proyecto_Ofertas_Empleo."
        )
    return genai.Client(api_key=api_key)

client = get_client()

# ============= CARGA CUOC =============

def cargar_cuoc_resumen() -> str:
    """
    Lee la tabla CUOC y devuelve un string resumido (codigo - titulo) de las primeras N filas.
    Si no hay filas útiles o hay error, simplemente devuelve "" y se omite CUOC en el prompt.
    """
    if not CUOC_INDEX_PATH.exists():
        print(f"⚠️ No se encontró el archivo CUOC en {CUOC_INDEX_PATH}. Se omitirá CUOC en el prompt.")
        return ""

    try:
        df = pd.read_excel(CUOC_INDEX_PATH)
        cols = df.columns[:2]
        df_simple = df[cols].dropna().head(MAX_FILAS_CUOC)

        if df_simple.empty:
            print("⚠️ CUOC cargado pero sin filas utilizables (0 filas).")
            return ""

        lineas = [
            f"{row[cols[0]]} - {row[cols[1]]}"
            for _, row in df_simple.iterrows()
        ]
        texto_cuoc = "\n".join(lineas)
        print(f"📑 CUOC cargado ({len(df_simple)} filas usadas en el prompt).")
        return texto_cuoc

    except Exception as e:
        print(f"⚠️ Error leyendo CUOC ({e}). Se omitirá CUOC en el prompt.")
        return ""

CUOC_RESUMEN = cargar_cuoc_resumen()

# ============= FUNCIONES AUXILIARES =============

def limpiar_texto(texto: str) -> str:
    """Quita espacios raros, saltos de línea duplicados, etc."""
    if not texto:
        return ""
    t = texto.replace("\r", " ").replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def es_texto_valido(texto: str) -> bool:
    """Descarta mensajes que son solo emojis / símbolos."""
    return bool(re.search(r"[A-Za-zÁÉÍÓÚáéíóúñÑ0-9]", texto or ""))

# ============= SOLO GEMINI (SIN REGLAS) =============

def clasificar_con_llm(oferta: dict) -> dict:
    """
    Usa el modelo de Gemini para clasificar.
    Devuelve dict: {
        "categoria": str,
        "subcategoria": str,
        "confianza": float,
        "cuoc_codigo": str,
        "cuoc_titulo": str
    }
    Si falla la API o el parseo, devuelve todo "Sin clasificar".
    """
    texto = oferta.get("contenido_limpio") or oferta.get("contenido") or ""
    texto = limpiar_texto(texto)

    cargo = limpiar_texto(oferta.get("cargo") or "")
    nivel = limpiar_texto(oferta.get("nivel_educativo") or "")
    tipo_contrato = limpiar_texto(oferta.get("tipo_contrato") or "")
    experiencia = limpiar_texto(oferta.get("experiencia") or "")
    ubicacion = limpiar_texto(oferta.get("ubicacion") or "")
    salario = limpiar_texto(str(oferta.get("salario") or ""))

    system_instrucciones = (
        "Eres un asistente experto en mercado laboral colombiano y en la "
        "clasificacion CUOC de profesiones. "
        "Tu tarea es clasificar ofertas de empleo en categorias predefinidas "
        "y, ademas, sugerir un codigo CUOC aproximado. "
        "RESPONDE SIEMPRE SOLO CON UN JSON VALIDO, sin ningun texto extra."
    )

    user_prompt = f"""
Clasifica la siguiente oferta de empleo en EXACTAMENTE UNA de estas categorias:

{", ".join(CATEGORIES)}

Ademas, usando la clasificacion de profesiones de Colombia (CUOC),
elige el codigo CUOC mas probable para la ocupacion descrita.

TABLA CUOC (parcial, codigo - titulo):
{CUOC_RESUMEN if CUOC_RESUMEN else "[No disponible]"}

Responde SOLO en JSON con este formato exacto (sin comentarios ni texto antes o despues):
{{
  "categoria": "una de las categorias de la lista",
  "subcategoria": "una etiqueta mas especifica o vacia",
  "confianza": 0.0 a 1.0,
  "cuoc_codigo": "codigo CUOC mas probable o vacio",
  "cuoc_titulo": "titulo CUOC asociado o vacio"
}}

Si el texto describe una feria, rueda de empleo, curso o evento informativo,
usa siempre la categoria "Evento/Curso (no empleo)".

TEXTO COMPLETO:
"{texto}"

Metadatos:
- cargo: "{cargo}"
- nivel_educativo: "{nivel}"
- tipo_contrato: "{tipo_contrato}"
- experiencia: "{experiencia}"
- ubicacion: "{ubicacion}"
- salario: "{salario}"
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                system_instrucciones,
                user_prompt,
            ],
        )

        raw = (response.text or "").strip()

        print("===== RAW GEMINI RESPONSE =====")
        print(repr(raw))
        print("================================")

        if not raw:
            raise ValueError("Gemini devolvió una respuesta vacía.")

        # 1) quitar fences tipo ```json ... ```
        if raw.startswith("```"):
            # elimina el inicio ```json o ``` + salto de linea
            raw = re.sub(r"^```[a-zA-Z0-9]*\s*", "", raw)
            # elimina el cierre ```
            raw = re.sub(r"```$", "", raw).strip()

        # 2) si aun asi hay texto alrededor, intenta extraer el primer bloque {...}
        json_str = None
        raw_stripped = raw.lstrip()
        if raw_stripped.startswith("{"):
            json_str = raw_stripped
        else:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                json_str = m.group(0)

        if not json_str:
            raise ValueError("La respuesta de Gemini no contiene un JSON reconocible.")

        data = json.loads(json_str)

        categoria = data.get("categoria", "Sin clasificar")
        subcategoria = data.get("subcategoria", "")
        confianza = float(data.get("confianza", 0.0))
        cuoc_codigo = data.get("cuoc_codigo", "")
        cuoc_titulo = data.get("cuoc_titulo", "")

    except Exception as e:
        print(f"⚠️ Error llamando a Gemini o parseando JSON ({e}).")
        categoria = "Sin clasificar"
        subcategoria = ""
        confianza = 0.0
        cuoc_codigo = ""
        cuoc_titulo = ""

    # Forzar que la categoría sea una de las nuestras si se desvió
    if categoria not in CATEGORIES:
        categoria = "Sin clasificar"

    return {
        "categoria": categoria,
        "subcategoria": subcategoria,
        "confianza": confianza,
        "cuoc_codigo": cuoc_codigo,
        "cuoc_titulo": cuoc_titulo,
    }

# ============= PIPELINE PRINCIPAL =============

def main():
    # 1. Cargar JSON original
    with open(RUTA_JSON_ENTRADA, "r", encoding="utf-8") as f:
        data = json.load(f)

    ofertas = data.get("ofertas_detalladas", [])
    print(f"📦 Ofertas cargadas: {len(ofertas)}")

    nuevas_ofertas = []
    llm_calls = 0

    # 2. Recorrer ofertas y clasificar
    for idx, oferta in enumerate(ofertas, start=1):
        texto = limpiar_texto(oferta.get("contenido_limpio") or oferta.get("contenido") or "")

        if not es_texto_valido(texto):
            oferta["categoria_llm"] = None
            oferta["subcategoria"] = ""
            oferta["confianza_llm"] = 0.0
            oferta["categoria_final"] = "Sin clasificar"
            oferta["cuoc_codigo"] = ""
            oferta["cuoc_titulo"] = ""
            nuevas_ofertas.append(oferta)
            continue

        usar_llm = llm_calls < MAX_LLM_CALLS

        if usar_llm:
            print(f"🔍 [{idx}] Clasificando con Gemini (llamadas usadas: {llm_calls+1}/{MAX_LLM_CALLS})")
            resultado_llm = clasificar_con_llm(oferta)
            llm_calls += 1
        else:
            resultado_llm = {
                "categoria": "Sin clasificar",
                "subcategoria": "",
                "confianza": 0.0,
                "cuoc_codigo": "",
                "cuoc_titulo": "",
            }

        categoria_llm = resultado_llm["categoria"]
        subcategoria = resultado_llm["subcategoria"]
        confianza = resultado_llm["confianza"]
        cuoc_codigo = resultado_llm["cuoc_codigo"]
        cuoc_titulo = resultado_llm["cuoc_titulo"]

        # Como solo estamos probando Gemini, la categoria_final = categoria_llm
        categoria_final = categoria_llm

        oferta["categoria_llm"] = categoria_llm
        oferta["subcategoria"] = subcategoria
        oferta["confianza_llm"] = confianza
        oferta["categoria_final"] = categoria_final
        oferta["cuoc_codigo"] = cuoc_codigo
        oferta["cuoc_titulo"] = cuoc_titulo

        nuevas_ofertas.append(oferta)

    # 3. Construir JSON de salida
    data_salida = dict(data)
    data_salida["ofertas_detalladas"] = nuevas_ofertas

    with open(RUTA_JSON_SALIDA, "w", encoding="utf-8") as f:
        json.dump(data_salida, f, ensure_ascii=False, indent=2)

    print(f"✅ Clasificación terminada. Archivo guardado en: {RUTA_JSON_SALIDA}")
    print(f"ℹ️ Llamadas a Gemini realizadas: {llm_calls} (MAX_LLM_CALLS = {MAX_LLM_CALLS})")

if __name__ == "__main__":
    main()
