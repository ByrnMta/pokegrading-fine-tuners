from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from Base_de_Datos.db import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    nombre = Column(String(80), nullable=False)
    apellidos = Column(String(120), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    contrasena = Column(String(100), nullable=False)
