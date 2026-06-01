from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from Base_de_Datos.db import Base

class EvaluacionCarta(Base):
    __tablename__ = "evaluacion_carta"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, nullable=False)
    toma_frontal_path = Column(String, nullable=False)
    toma_reversa_path = Column(String, nullable=False)
    fecha_evaluacion = Column(DateTime(timezone=True), server_default=func.now())
