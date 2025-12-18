from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True) # unique=True: No puede haber dos emails iguales
    
    # RELACIÓN:
    # Esto dice: "Mis productos están en la tabla Producto, conectados por el campo 'owner'"
    productos = relationship("Producto", back_populates="propietario")

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    precio = Column(Float)
    en_oferta = Column(Boolean, default=False)
    
    # CLAVE FORÁNEA (El vínculo real en la base de datos)
    # Esto guarda el ID del usuario (ej: 1, 2, 55)
    propietario_id = Column(Integer, ForeignKey("usuarios.id"))

    # RELACIÓN (El vínculo mágico de Python)
    # Nos permite acceder a 'producto.propietario' y ver los datos del usuario directamente
    propietario = relationship("Usuario", back_populates="productos")