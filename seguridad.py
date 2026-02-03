from passlib.context import CryptContext

# Configuración del algoritmo de encriptación (usamos bcrypt, el estándar industrial)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función 1: TRITURAR (Crear el Hash)
# Tú le das "secreto" -> Ella devuelve "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn3ILA..."
def get_password_hash(password):
    return pwd_context.hash(password)

# Función 2: VERIFICAR
# Compara una contraseña plana con el hash guardado
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)