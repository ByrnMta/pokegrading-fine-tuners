from sqlalchemy import Column, Integer, String, Float
from Datos.db import Base


class BaselineCalibracion(Base):
    __tablename__ = "baseline_calibracion"

    id = Column(Integer, primary_key=True, index=True)
    set_name = Column(String(100), nullable=True)  # NULL → baseline global
    acabado = Column(String(50), nullable=True)  # NULL → baseline global
    centering_baseline = Column(Float, nullable=False)
    corners_baseline = Column(Float, nullable=False)
    edges_baseline = Column(Float, nullable=False)
    surface_baseline = Column(Float, nullable=False)
    total_muestras = Column(Integer, nullable=False)
    confianza = Column(Float, nullable=False)  # 0.0 – 1.0
