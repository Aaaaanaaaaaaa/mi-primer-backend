import sqlite3 # <--- Importamos esto
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    nombre: str
    precio: float

@app.post("/items")
def crear_item(nuevo_item: Item):
    # 1. Conectamos a la base de datos que acabamos de crear
    conexion = sqlite3.connect("mi_tienda.db")
    cursor = conexion.cursor()
    
    # 2. INSERTAR DATOS (Comando SQL)
    # Los interrogantes (?) son por seguridad (evitan hackeos SQL Injection)
    cursor.execute("INSERT INTO productos (nombre, precio) VALUES (?, ?)", 
                   (nuevo_item.nombre, nuevo_item.precio))
    
    conexion.commit() # Guardar cambios
    conexion.close()  # Cerrar conexión
    
    return {"mensaje": "Producto guardado en la Base de Datos", "producto": nuevo_item}


@app.get("/items")
def ver_todos_los_items():
    # 1. Conectar
    conexion = sqlite3.connect("mi_tienda.db")
    
    # 2. Configurar para que nos devuelva diccionarios (opcional pero recomendado)
    # Esto hace que en vez de devolver (1, "Teclado", 50), devuelva {"nombre": "Teclado"...}
    # Pero por ahora lo haremos simple, raw data.
    cursor = conexion.cursor()
    
    # 3. EJECUTAR SELECT (Leer datos)
    cursor.execute("SELECT * FROM productos")
    
    # 4. CAPTURAR RESULTADOS
    productos_guardados = cursor.fetchall()
    
    conexion.close()
    
    return {"inventario": productos_guardados}


@app.delete("/items/{item_id}")
def borrar_item(item_id: int):
    conexion = sqlite3.connect("mi_tienda.db")
    cursor = conexion.cursor()
    
    # 1. Intentamos borrar el producto con ese ID
    cursor.execute("DELETE FROM productos WHERE id = ?", (item_id,))
    
    # 2. Guardamos cambios
    conexion.commit()
    
    # 3. Verificamos si se borró algo (rowcount nos dice cuántas filas afectó)
    filas_borradas = cursor.rowcount
    conexion.close()
    
    if filas_borradas > 0:
        return {"mensaje": f"Producto {item_id} eliminado correctamente"}
    else:
        return {"mensaje": "No se encontró ningún producto con ese ID"}
    
@app.put("/items/{item_id}")
def actualizar_item(item_id: int, item_actualizado: Item):
    conexion = sqlite3.connect("mi_tienda.db")
    cursor = conexion.cursor()
    
    # Actualizamos nombre y precio donde el ID coincida
    cursor.execute(
        "UPDATE productos SET nombre = ?, precio = ? WHERE id = ?",
        (item_actualizado.nombre, item_actualizado.precio, item_id)
    )
    
    conexion.commit()
    conexion.close()
    
    return {"mensaje": f"Producto {item_id} actualizado", "nuevos_datos": item_actualizado}