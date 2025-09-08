
import re
from hashlib import sha1
from datetime import datetime
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?\d{7,12}")
URL_RE = re.compile(r"https?://\S+")
SAL_RE = re.compile(r"\b(?:salario|pago|remuneraci[óo]n|sueldo)[:\s]*([\d\.\,\$kKmM ]+)", re.I)
UBI_RE = re.compile(r"\b(?:ubicaci[óo]n|lugar|ciudad|modalidad)[:\s]*([A-Za-zÁÉÍÓÚÑ\s/\-]+)", re.I)
EMP_RE = re.compile(r"\b(?:empresa|compañ[ií]a|firma)[:\s]*([A-Za-zÁÉÍÓÚÑ&\s/\-]+)", re.I)
TITLE_HINTS = ("analista", "cient", "data", "analyst", "engineer", "developer", "ingenier", "intern", "practic", "estudiante", "estadíst")

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def parse_message(text: str, chat_name: str, ts: datetime):
    # Si llega HTML, normaliza
    text = BeautifulSoup(text, "html.parser").get_text("\n")
    texto = _clean(text)

    emails = EMAIL_RE.findall(texto)
    phones = PHONE_RE.findall(texto)
    urls = URL_RE.findall(texto)

    salario = None
    m = SAL_RE.search(texto);  salario = _clean(m.group(1)) if m else None

    ubicacion = None
    m = UBI_RE.search(texto);  ubicacion = _clean(m.group(1)) if m else None

    empresa = None
    m = EMP_RE.search(texto);   empresa = _clean(m.group(1)) if m else None

    # Heurística para título
    titulo = None
    for line in texto.split("\n"):
        ls = line.lower()
        if any(h in ls for h in TITLE_HINTS) and 6 <= len(line) <= 120:
            titulo = _clean(line); break

    contacto = (emails[0] if emails else None) or (phones[0] if phones else None)
    urls_s = " ".join(urls[:5]) if urls else None

    # Hash único (chat + snippet + minuto)
    id_ = sha1(f"{chat_name}|{texto[:280]}|{ts.strftime('%Y-%m-%d %H:%M')}".encode("utf-8")).hexdigest()

    return {
        "id": id_,
        "ts_iso": ts.isoformat(timespec="seconds"),
        "fuente": chat_name,
        "texto_original": texto,
        "titulo": titulo,
        "empresa": empresa,
        "ubicacion": ubicacion,
        "salario": salario,
        "contacto": contacto,
        "urls": urls_s
    }
