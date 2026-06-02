from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from Datos.db import Base

class EvaluacionCarta(Base):
    __tablename__ = "evaluacion_carta"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    toma_frontal_path = Column(String, nullable=True)
    toma_reversa_path = Column(String, nullable=True)
    fecha_evaluacion = Column(DateTime(timezone=True), server_default=func.now())
