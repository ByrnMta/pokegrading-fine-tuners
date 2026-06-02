from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from Datos.db import Base

# Modelo de Rol, con sus atributos y relaciones (para la base de datos)
class Rol(Base):
    __tablename__ = "rol"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200), nullable=True)

    # Relación con Usuario
    # se coloca el nombre de la clase Usuario, no el nombre de la tabla, y se agrega backref para facilitar el acceso desde Usuario a Rol
    usuarios = relationship("Usuario", backref="rol")