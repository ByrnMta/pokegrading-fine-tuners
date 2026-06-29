from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Datos.db import Base


class ResultadoCalificacionCarta(Base):
    __tablename__ = "resultado_calificacion_carta"

    id = Column(Integer, primary_key=True, index=True)
    id_evaluacionCarta = Column(
        Integer, ForeignKey("evaluacion_carta.id"), nullable=False
    )
    id_sesion = Column(String(100), nullable=False)
    huella_imagenes = Column(String(64), nullable=True, index=True)  # SHA-256 hex digest de (frontal + reversa)
    version_algoritmo = Column(String(20), nullable=False)
    centering_subgrade = Column(Float, nullable=True)
    corners_subgrade = Column(Float, nullable=True)
    edges_subgrade = Column(Float, nullable=True)
    surface_subgrade = Column(Float, nullable=True)
    grado_final = Column(Float, nullable=True)
    uncertainty_band = Column(Float, nullable=True)
    baseline_origen = Column(String(20), nullable=False)  # "GLOBAL" | "SET_ACABADO"
    baseline_centering = Column(Float, nullable=True)
    baseline_corners = Column(Float, nullable=True)
    baseline_edges = Column(Float, nullable=True)
    baseline_surface = Column(Float, nullable=True)
    tipo_revision = Column(String(20), nullable=False)  # "AUTO" | "MANUAL" | "REVIEW"
    coherence_flag = Column(String(20), nullable=False)  # "OK" | "REVIEW"
    fecha_calificacion = Column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relación con evaluacion_carta
    evaluacion_carta = relationship("EvaluacionCarta", backref="resultado_calificacion")

    # Garantiza idempotencia: mismo par (evaluacion, sesion) no se duplica
    __table_args__ = (
        UniqueConstraint(
            "id_evaluacionCarta",
            "id_sesion",
            name="uq_evaluacion_sesion",
        ),
    )