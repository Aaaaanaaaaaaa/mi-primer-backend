from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt #librería para generar los Tokens

# --- Configuración ---
#Generamos la "firma secreta" tokens
SECRET_KEY = "esto-deberia-ser-super-secreto-y-largo" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#configuración de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función 1: Hash (triturar)
def get_password_hash(password):
    return pwd_context.hash(password)

# Función 2: Verificar (Comparar)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#Función 3: crear token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    #Creamos el token cifrado con nuestra clave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt