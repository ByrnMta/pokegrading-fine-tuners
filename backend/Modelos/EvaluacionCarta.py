from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Datos.db import Base

class EvaluacionCarta(Base):
    __tablename__ = "evaluacion_carta"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    toma_frontal_path = Column(String, nullable=True)
    toma_reversa_path = Column(String, nullable=True)
    estado = Column(String(20), nullable=False, default="PENDIENTE")  # PENDIENTE | COMPLETADA | MANUAL | REVIEW

    fecha_evaluacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con preprocesado de carta
    # se coloca el nombre de la clase PreprocesadoCarta, no el nombre de la tabla, y se agrega backref para facilitar el acceso desde PreprocesadoCarta a EvaluacionCarta
    preprocesado_carta = relationship("PreprocesadoCarta", backref="evaluacion_carta")
