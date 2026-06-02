from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from Base_de_Datos.db import Base

class Carta(Base):
    __tablename__ = "cartas"

    """Tabla principal de cartas del catálogo."""

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(String(36), unique=True, index=True, nullable=False)
    numero = Column(String(50), nullable=False)
    set_name = Column(String(100), nullable=False)
    edicion = Column(String(100), nullable=False)
    idioma = Column(String(50), nullable=False)
    acabado = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=True)
    rareza = Column(String(50), nullable=True)
    tipo = Column(String(50), nullable=True)
    hp = Column(Integer, nullable=True)
    ilustrador = Column(String(100), nullable=True)
    anio_impresion = Column(Integer, nullable=True)
    autor = Column(String(100), nullable=False)
    estado = Column(String(50), default="ACTIVA")
    image_front_path = Column(String(255), nullable=False)
    image_back_path = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())