from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import modelos as modelos # OJO: Asegúrate de que importas tus modelos
import database
import seguridad

app = FastAPI()

# --- 1. ESQUEMAS PYDANTIC (Validación de entrada) ---
# Esquema para crear Productos
class ItemSchema(BaseModel):
    nombre: str
    precio: float
    en_oferta: bool = False
    # owner_id: int  <-- Podríamos poner esto si quisiéramos verlo
    
    class Config:
        from_attributes = True

class UsuarioSchema(BaseModel):
    nombre: str
    email: str
    password: str # <--- Nuevo campo (Texto plano que envía el usuario)
    # productos: list[ItemSchema] = [] # <-- Esto quítalo de aquí, luego te explico por qué (*)

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
    # 1. TRITURAMOS LA CONTRASEÑA 
    password_segura = seguridad.get_password_hash(usuario.password)
    
    # 2. Creamos el usuario con la contraseña YA hasheada
    # Fíjate: guardamos en 'hashed_password' lo que salió de la trituradora
    nuevo_usuario = modelos.Usuario(
        nombre=usuario.nombre, 
        email=usuario.email,
        hashed_password=password_segura 
    )
    
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

# FÍJATE AQUÍ: Añadimos response_model=UsuarioSchema
# Esto obliga a FastAPI a mirar tu esquema, ver que hay una lista de 'productos',
# y buscar esos datos en la base de datos automáticamente.
@app.get("/usuarios/{user_id}", response_model=UsuarioSchema)
def leer_usuario(user_id: int, db: Session = Depends(get_db)):
    usuario = db.query(modelos.Usuario).filter(modelos.Usuario.id == user_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario