import sqlite3

conn = sqlite3.connect("whatsapp.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM mensajes;")   # Borra todos los registros
conn.commit()
conn.close()