import os
import json
import re
from pathlib import Path
from openai import OpenAI, RateLimitError  
from dotenv import load_dotenv

# === Cargar .env desde la carpeta del proyecto ===

SCRIPT_DIR = Path(__file__).resolve().parent  # carpeta Proyecto_Ofertas_Empleo
DOTENV_PATH = SCRIPT_DIR / ".env"

load_dotenv(dotenv_path=DOTENV_PATH)
print(f"[DEBUG] Usando .env en: {DOTENV_PATH}")

# ============= CONFIG =============
RUTA_JSON_ENTRADA = SCRIPT_DIR / "analisis_ofertas_empleo.json"
RUTA_JSON_SALIDA = SCRIPT_DIR / "analisis_ofertas_empleo_clasificado.json"

# Modelo válido de la API
OPENAI_MODEL = "gpt-5o"

# Categorías que vamos a usar
CATEGORIES = [
    "Call center/BPO",
    "Logística/Bodega",
    "Salud",
    "Retail/Comercial",
    "Tecnología/Ingeniería",
    "Administrativo/Facturación",
    "Conducción/Operaciones",
    "Evento/Curso (no empleo)"
]

# Reglas simples por palabras clave (en minúsculas)
RULES = {
    "Call center/BPO": [
        r"\bcall\s*center\b", r"\bcontact\s*center\b", r"\basesor(?:es)?\b",
        r"\bbpo\b"
    ],
    "Logística/Bodega": [
        r"\bbodega\b", r"\blog[ií]stic", r"\boperari[oa]s?\b", r"\bplanta\b"
    ],
    "Salud": [
        r"\benfermer", r"\bsalud p[úu]blica\b", r"\bsubred\b", r"\bhospital\b"
    ],
    "Retail/Comercial": [
        r"\bventas?\b", r"\btienda\b", r"\bmercaderist", r"\bcajer[oa]s?\b"
    ],
    "Tecnología/Ingeniería": [
        r"\bdesarrollador(?:es)?\b", r"\bprogramador(?:es)?\b",
        r"\bingenier[oa]\b", r"\bpreventa\b", r"\bsistemas\b", r"\bsoftware\b"
    ],
    "Administrativo/Facturación": [
        r"\bauxiliar administrativo\b", r"\bfacturaci[oó]n\b",
        r"\bgesti[oó]n documental\b"
    ],
    "Conducción/Operaciones": [
        r"\bconductor(?:es)?\b", r"\bC2\b", r"\bC3\b",
        r"\boperaciones\b", r"\bparqueadero\b"
    ],
    "Evento/Curso (no empleo)": [
        r"\bferia\b", r"\bcurso\b", r"\bru[eé]da de empleo\b",
        r"\breg[ií]strate\b", r"\binscr[ií]bete\b", r"\bcharla\b"
    ]
}

# ============= CLIENTE OPENAI =============
def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No se encontró la variable de entorno OPENAI_API_KEY. "
            "Crea un archivo .env o define la variable en tu sistema."
        )
    return OpenAI(api_key=api_key)

client = get_client()

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

def aplicar_reglas(texto: str) -> str | None:
    """Devuelve categoría por reglas, o None si no matchea nada."""
    if not texto:
        return None
    texto_l = texto.lower()
    for categoria, patrones in RULES.items():
        for patron in patrones:
            if re.search(patron, texto_l):
                return categoria
    return None

def clasificar_con_llm(oferta: dict, categoria_reglas: str | None) -> dict:
    """
    Usa el modelo de OpenAI para clasificar.
    Devuelve dict: {"categoria": str, "subcategoria": str, "confianza": float}
    Si falla la API (por ejemplo, por falta de cuota), hace fallback a las reglas.
    """
    texto = oferta.get("contenido_limpio") or oferta.get("contenido") or ""
    texto = limpiar_texto(texto)

    cargo = limpiar_texto(oferta.get("cargo") or "")
    nivel = limpiar_texto(oferta.get("nivel_educativo") or "")
    tipo_contrato = limpiar_texto(oferta.get("tipo_contrato") or "")
    experiencia = limpiar_texto(oferta.get("experiencia") or "")
    ubicacion = limpiar_texto(oferta.get("ubicacion") or "")
    salario = limpiar_texto(str(oferta.get("salario") or ""))

    system_prompt = (
        "Eres un asistente experto en mercado laboral colombiano. "
        "Tu tarea es clasificar ofertas de empleo en categorias predefinidas. "
        "Responde SIEMPRE en JSON valido."
    )

    user_prompt = f"""
Clasifica la siguiente oferta de empleo en EXACTAMENTE UNA de estas categorias:

{", ".join(CATEGORIES)}

Responde SOLO en JSON con este formato exacto:
{{
  "categoria": "una de las categorias de la lista",
  "subcategoria": "una etiqueta mas especifica o vacia",
  "confianza": 0.0 a 1.0
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

Categoria sugerida por reglas (puede estar vacia): "{categoria_reglas}"
"""

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # Texto bruto devuelto por el modelo
        try:
            raw = response.output_text
        except AttributeError:
            try:
                raw = response.output[0].content[0].text
            except Exception:
                raw = ""

        data = json.loads(raw)
        categoria = data.get("categoria")
        subcategoria = data.get("subcategoria", "")
        confianza = float(data.get("confianza", 0.0))

    except RateLimitError:
        print("⚠️ Sin cuota en OpenAI, usando solo reglas para esta oferta.")
        categoria = categoria_reglas or "Sin clasificar"
        subcategoria = ""
        confianza = 0.0

    except Exception as e:
        print(f"⚠️ Error llamando al LLM ({e}), usando solo reglas.")
        categoria = categoria_reglas or "Sin clasificar"
        subcategoria = ""
        confianza = 0.0

    # Forzar que la categoría sea una de las nuestras si se desvió
    if categoria not in CATEGORIES:
        if categoria_reglas in CATEGORIES:
            categoria = categoria_reglas
        else:
            categoria = "Evento/Curso (no empleo)" if "feria" in texto.lower() else "Sin clasificar"

    return {
        "categoria": categoria,
        "subcategoria": subcategoria,
        "confianza": confianza,
    }

# ============= PIPELINE PRINCIPAL =============

def main():
    # 1. Cargar JSON original
    with open(RUTA_JSON_ENTRADA, "r", encoding="utf-8") as f:
        data = json.load(f)

    ofertas = data.get("ofertas_detalladas", [])
    print(f"📦 Ofertas cargadas: {len(ofertas)}")

    # 2. Recorrer ofertas y clasificar
    nuevas_ofertas = []
    for oferta in ofertas:
        texto = limpiar_texto(oferta.get("contenido_limpio") or oferta.get("contenido") or "")
        if not es_texto_valido(texto):
            oferta["categoria_reglas"] = None
            oferta["categoria_llm"] = None
            oferta["confianza_llm"] = 0.0
            oferta["categoria_final"] = "Sin clasificar"
            nuevas_ofertas.append(oferta)
            continue

        categoria_reglas = aplicar_reglas(texto)
        resultado_llm = clasificar_con_llm(oferta, categoria_reglas)
        categoria_llm = resultado_llm["categoria"]
        subcategoria = resultado_llm["subcategoria"]
        confianza = resultado_llm["confianza"]

        if confianza >= 0.7:
            categoria_final = categoria_llm
        elif categoria_reglas:
            categoria_final = categoria_reglas
        else:
            categoria_final = categoria_llm

        oferta["categoria_reglas"] = categoria_reglas
        oferta["categoria_llm"] = categoria_llm
        oferta["subcategoria"] = subcategoria
        oferta["confianza_llm"] = confianza
        oferta["categoria_final"] = categoria_final

        nuevas_ofertas.append(oferta)

    data_salida = dict(data)
    data_salida["ofertas_detalladas"] = nuevas_ofertas

    with open(RUTA_JSON_SALIDA, "w", encoding="utf-8") as f:
        json.dump(data_salida, f, ensure_ascii=False, indent=2)

    print(f"✅ Clasificación terminada. Archivo guardado en: {RUTA_JSON_SALIDA}")

if __name__ == "__main__":
    main()



