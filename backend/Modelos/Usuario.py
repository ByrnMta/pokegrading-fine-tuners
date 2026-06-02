from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Datos.db import Base


# Modelo de usuario, con sus atributos y relaciones (para la base de datos)
class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True)
    rol_id = Column(Integer, ForeignKey("rol.id"), nullable=False)
    pais_id = Column(Integer, ForeignKey("pais.id"), nullable=False)
    idioma_id = Column(Integer, ForeignKey("idioma.id"), nullable=False)
    nombre_usuario = Column(String(80), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    contrasena = Column(String(100), nullable=False)
    ultimo_acceso = Column(DateTime(timezone=True), nullable=True, server_default=func.now())

    # Relación con evaluación de carta
    # se coloca el nombre de la clase Usuario, no el nombre de la tabla, y se agrega backref para facilitar el acceso desde Usuario a EvaluacionCarta
    evaluaciones_carta = relationship("EvaluacionCarta", backref="usuario")
    