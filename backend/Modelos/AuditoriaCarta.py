from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from Base_de_Datos.db import Base

"""Modelo ORM para la auditoría de altas de cartas."""


class AuditoriaCarta(Base):
    __tablename__ = "auditoria_cartas"

    """Tabla que conserva el evento de alta y el payload registrado."""

    id = Column(Integer, primary_key=True, index=True)
    carta_id = Column(Integer, ForeignKey("cartas.id"), nullable=False)
    card_id = Column(String(36), index=True, nullable=False)
    autor = Column(String(100), nullable=False)
    accion = Column(String(50), nullable=False, default="ALTA")
    datos_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
