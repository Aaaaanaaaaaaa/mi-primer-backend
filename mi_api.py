from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import modelos as modelos # OJO: Asegúrate de que importas tus modelos
import database

app = FastAPI()

# --- 1. ESQUEMAS PYDANTIC (Validación de entrada) ---

# Esquema para crear Usuarios
class UsuarioSchema(BaseModel):
    nombre: str
    email: str
    
    class Config:
        from_attributes = True

# Esquema para crear Productos
class ItemSchema(BaseModel):
    nombre: str
    precio: float
    en_oferta: bool = False
    
    class Config:
        from_attributes = True

# --- 2. DEPENDENCIA DE BASE DE DATOS ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. RUTAS (ENDPOINTS) ---

# RUTA NUEVA: Crear Usuario 👤
@app.post("/usuarios")
def crear_usuario(usuario: UsuarioSchema, db: Session = Depends(get_db)):
    # Creamos el objeto Usuario de la base de datos
    nuevo_usuario = modelos.Usuario(nombre=usuario.nombre, email=usuario.email)
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

# RUTA MODIFICADA: Crear Producto asignado a un Usuario 📦
# Fíjate: Añadimos 'user_id' a la ruta para saber de quién es el producto
@app.post("/usuarios/{user_id}/items")
def crear_item_para_usuario(user_id: int, item: ItemSchema, db: Session = Depends(get_db)):
    
    # PASO 1: Verificar que el usuario existe (Buena práctica)
    usuario = db.query(modelos.Usuario).filter(modelos.Usuario.id == user_id).first()
    
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # PASO 2: Crear el producto vinculándolo al ID del usuario
    nuevo_item = modelos.Producto(
        nombre=item.nombre,
        precio=item.precio,
        en_oferta=item.en_oferta,
        propietario_id=user_id  # <--- AQUÍ ESTÁ LA MAGIA DE LA RELACIÓN
    )
    
    db.add(nuevo_item)
    db.commit()
    db.refresh(nuevo_item)
    
    return nuevo_item

# RUTA GET: Ver todos los productos (y verás que incluyen el ID de su dueño)
@app.get("/items")
def leer_items(db: Session = Depends(get_db)):
    items = db.query(modelos.Producto).all()
    return items