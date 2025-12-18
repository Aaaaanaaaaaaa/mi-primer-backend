import database
import modelos

# ESTA ES LA LÍNEA MÁGICA ✨
# Le dice a SQLAlchemy: 
# "Ve a 'modelos', mira todas las clases que hereden de Base, 
# y crea las tablas correspondientes en el motor 'database.engine'".
modelos.Base.metadata.create_all(bind=database.engine)

print("¡Tablas creadas exitosamente en 'mi_tienda_profesional.db'!")