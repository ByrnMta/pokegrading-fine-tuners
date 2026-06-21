from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from Datos.db import Base

class RespuestaCacheada(Base):
    __tablename__ = "respuesta_cacheada"

    id = Column(Integer, primary_key=True, index=True)
    tienda_id = Column(String(255), unique=True, index=True, nullable=False) # ID propio que brinda la tienda
    respuesta_body = Column(JSON, nullable=False) # la respuesta en formato JSON
    # Timestamp para controlar la ventana de tiempo
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)