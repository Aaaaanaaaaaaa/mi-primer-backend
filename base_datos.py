import sqlite3

# 1. CONECTAR (Si el archivo no existe, lo crea automáticamente)
conexion = sqlite3.connect("mi_tienda.db")

# 2. EL CURSOR (Es el "lápiz" para escribir en la base de datos)
cursor = conexion.cursor()

# 3. CREAR TABLA (Escribimos código SQL)
# IF NOT EXISTS: Para que no de error si ejecutas el script dos veces.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL
    )
""")

# 4. GUARDAR CAMBIOS Y CERRAR
conexion.commit()
conexion.close()

print("Base de datos y tabla creadas con éxito.")   