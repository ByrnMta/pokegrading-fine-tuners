
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from Datos.db import Base

class PreprocesadoCarta(Base):
    __tablename__ = "preprocesado_carta"

    id = Column(Integer, primary_key=True, index=True)
    id_evaluacionCarta = Column(Integer, ForeignKey("evaluacion_carta.id"), nullable=False)
    tipo_revision = Column(String(20), nullable=False) # Si es "AUTO" o "MANUAL"
    centering_score = Column(Float, nullable=True)
    corner_score = Column(Float, nullable=True)
    edges_score = Column(Float, nullable=True)
    surface_score = Column(Float, nullable=True)
    tipo_imagen = Column(String(20), nullable=False)  # "FRONTAL" o "REVERSA"
