import sqlite3

# Conectar a la base de datos (esto crea whatsapp.db si no existe)
conn = sqlite3.connect("whatsapp.db")
cursor = conn.cursor()

# Crear tabla de mensajes si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        remitente TEXT,
        contenido TEXT,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

print("✅ Base de datos creada y lista para almacenar mensajes")

conn.commit()
conn.close()

conn = sqlite3.connect("whatsapp.db")
cursor = conn.cursor()

# Insertar un mensaje de prueba
cursor.execute("""
    INSERT INTO mensajes (remitente, contenido)
    VALUES (?, ?)
""", ("Juan", "Hola, este es un mensaje de prueba en la base de datos"))

# Confirmar cambios
conn.commit()



