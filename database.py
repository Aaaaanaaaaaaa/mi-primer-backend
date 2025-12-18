from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. URL de la base de datos (igual que antes, un archivo local)
DATABASE_URL = "sqlite:///./mi_tienda_profesional.db"

# 2. Crear el Motor (Engine)
# connect_args={"check_same_thread": False} es necesario SOLO para SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 3. Crear la Sesión (Es lo que usaremos para guardar/borrar datos)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base para los Modelos
# Todas nuestras clases heredarán de aquí para convertirse en tablas
Base = declarative_base()