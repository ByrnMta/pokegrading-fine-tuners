from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from Base_de_Datos.db import Base


# Modelo de usuario, con sus atributos y relaciones (para la base de datos)
class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True)
    rol_id = Column(Integer, ForeignKey("rol.id"), nullable=False)
    nombre_usuario = Column(String(80), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    contrasena = Column(String(100), nullable=False)
