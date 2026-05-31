from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from Base_de_Datos.db import Base

# Modelo de País, con sus atributos y relaciones (para la base de datos)
class Pais(Base):
    __tablename__ = "pais"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)

    # Relación con Usuario
    # se coloca el nombre de la clase Usuario, no el nombre de la tabla, y se agrega backref para facilitar el acceso desde Usuario a Rol
    usuarios = relationship("Usuario", backref="pais") 