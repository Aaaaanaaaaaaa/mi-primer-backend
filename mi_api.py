from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importamos tus archivos nuevos
import modelos
import database

app = FastAPI()

# --- 1. CONFIGURACIÓN PYDANTIC (Lo que ve el usuario) ---
# Usamos esto para validar que nos envían los datos correctos.
class ItemSchema(BaseModel):
    nombre: str
    precio: float
    en_oferta: bool = False

    # Esta config es necesaria para que Pydantic se lleve bien con el ORM
    class Config:
        from_attributes = True

# --- 2. LA DEPENDENCIA (El Vendor) ---
# Esta función entrega la base de datos y la cierra al terminar
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. RUTAS (EndPoints) ---

# RUTA POST: Crear Producto
@app.post("/items")
def crear_item(item: ItemSchema, db: Session = Depends(get_db)):
    # FÍJATE EN LA MAGIA ✨:
    # Ya no escribimos SQL "INSERT INTO...".
    # Creamos un OBJETO del modelo (el de modelos.py) usando los datos del esquema.
    nuevo_producto = modelos.Producto(
        nombre=item.nombre, 
        precio=item.precio, 
        en_oferta=item.en_oferta
    )
    
    db.add(nuevo_producto)  # Lo añadimos a la sesión (como ponerlo en el carrito)
    db.commit()             # Confirmamos la compra (Guardar en DB)
    db.refresh(nuevo_producto) # Recargamos el objeto para tener su ID nuevo
    
    return nuevo_producto

# RUTA GET: Leer Productos
@app.get("/items")
def leer_items(db: Session = Depends(get_db)):
    # Ya no hay "SELECT * FROM".
    # Le decimos a la DB: "Dame todos los registros de la tabla Producto"
    items = db.query(modelos.Producto).all()
    return items

# RUTA DELETE: Borrar Producto
@app.delete("/items/{item_id}")
def borrar_item(item_id: int, db: Session = Depends(get_db)):
    # 1. Buscamos el producto por ID
    producto = db.query(modelos.Producto).filter(modelos.Producto.id == item_id).first()
    
    if producto is None:
        return {"error": "Producto no encontrado"}
    
    # 2. Lo borramos
    db.delete(producto)
    db.commit()
    
    return {"mensaje": "Producto eliminado"}