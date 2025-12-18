from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base # Importamos la base que acabamos de crear

class Producto(Base):
    __tablename__ = "productos" # Nombre de la tabla en la BD

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    precio = Column(Float)
    en_oferta = Column(Boolean, default=False)