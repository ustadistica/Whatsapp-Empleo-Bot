import sqlite3
import pandas as pd

# 1️⃣ Conecta a la base de datos
conn = sqlite3.connect("whatsapp.db")

# 2️⃣ Obtiene la lista de tablas
tablas = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

print("📋 Tablas encontradas:")
for nombre in tablas["name"]:
    print(f"- {nombre}")

# 3️⃣ Exporta cada tabla a un CSV
for nombre in tablas["name"]:
    df = pd.read_sql_query(f"SELECT * FROM {nombre}", conn)
    df.to_csv(f"{nombre}.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Tabla '{nombre}' exportada a '{nombre}.csv'")

conn.close()
print("🎉 Exportación completa.")
   
