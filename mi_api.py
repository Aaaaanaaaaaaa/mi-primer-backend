from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import modelos as modelos 
import database
import seguridad
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

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

# --- ESQUEMA SOLO PARA MOSTRAR DATOS (SALIDA) ---
# Fíjate que NO tiene el campo password. ¡Seguridad ante todo!
class UsuarioPublico(BaseModel):
    id: int
    nombre: str
    email: str
    productos: list[ItemSchema] = [] # Queremos ver sus productos

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

# 1. EL CERROJO 🔒
# Esto le dice a FastAPI: "Para entrar aquí, busca un token en la cabecera"
# Y si no hay, manda al usuario a la ruta "/token" para que se loguee.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 2. EL PORTERO (Verificar Token) 🦍
# Esta función coge el token, lo lee, y busca al usuario en la base de datos.
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificamos el token usando la clave secreta que está en seguridad.py
        payload = jwt.decode(token, seguridad.SECRET_KEY, algorithms=[seguridad.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Buscamos al usuario en la BD
    user = db.query(modelos.Usuario).filter(modelos.Usuario.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user
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

# RUTA LOGIN: El usuario da usuario/contraseña -> Recibe Token
@app.post("/token")
def login_para_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # NOTA: OAuth2PasswordRequestForm siempre guarda el usuario en "username" y la clave en "password".
    # Aunque nosotros usemos email, el formulario lo llama 'username'.
    
    # 1. BUSCAR AL USUARIO (Por email)
    usuario = db.query(modelos.Usuario).filter(modelos.Usuario.email == form_data.username).first()
    
    # 2. VERIFICAR SI EXISTE Y SI LA CLAVE ES CORRECTA
    if not usuario or not seguridad.verify_password(form_data.password, usuario.hashed_password):
        # Si falla algo, lanzamos error 401 (No autorizado)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. SI TODO ESTÁ OK: GENERAR TOKEN
    # Guardamos el email dentro del token (en el campo "sub")
    access_token = seguridad.create_access_token(data={"sub": usuario.email})
    
    # 4. DEVOLVER EL TOKEN
    return {"access_token": access_token, "token_type": "bearer"}

# RUTA PRIVADA: Ver mi propio perfil 🕵️‍♀️
# CAMBIO AQUÍ 👇: Usamos UsuarioPublico en lugar de UsuarioSchema
@app.get("/users/me", response_model=UsuarioPublico)
def read_users_me(current_user: modelos.Usuario = Depends(get_current_user)):
    return current_user