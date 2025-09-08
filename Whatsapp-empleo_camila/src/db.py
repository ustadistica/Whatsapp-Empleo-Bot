
import sqlite3
from pathlib import Path

# Base de datos SQLite en /db/ofertas.sqlite (carpeta del repo)
DB_PATH = Path(__file__).resolve().parents[1] / "db" / "ofertas.sqlite"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DDL = """
CREATE TABLE IF NOT EXISTS ofertas (
  id TEXT PRIMARY KEY,
  ts_iso TEXT,
  fuente TEXT,
  texto_original TEXT,
  titulo TEXT,
  empresa TEXT,
  ubicacion TEXT,
  salario TEXT,
  contacto TEXT,
  urls TEXT
);
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    return conn

def insert_oferta(row: dict) -> bool:
    with get_conn() as conn:
        try:
            conn.execute(
                """INSERT INTO ofertas
                (id, ts_iso, fuente, texto_original, titulo, empresa, ubicacion, salario, contacto, urls)
                VALUES (:id, :ts_iso, :fuente, :texto_original, :titulo, :empresa, :ubicacion, :salario, :contacto, :urls)""",
                row
            )
            return True
        except sqlite3.IntegrityError:
            return False

def export_csv():
    import pandas as pd
    out = Path(__file__).resolve().parents[1] / "data" / "ofertas.csv"
    with get_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM ofertas ORDER BY ts_iso DESC", conn)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
