from typing import Optional
from pydantic import BaseModel


class PreprocesadoCaraInfo(BaseModel):
    """Información del preprocesamiento de una cara (frontal/reversa)."""
    centering: Optional[float] = None
    corners: Optional[float] = None
    edges: Optional[float] = None
    surface: Optional[float] = None
    tipo_revision: str  # "AUTO" | "MANUAL"
    tipo_imagen: str    # "FRONTAL" | "REVERSA"


class ResultadoCalificacionOut(BaseModel):
    """Respuesta completa de la calificación de una carta."""
    version_algoritmo: str
    centering_subgrade: Optional[float] = None
    corners_subgrade: Optional[float] = None
    edges_subgrade: Optional[float] = None
    surface_subgrade: Optional[float] = None
    grado_final: Optional[float] = None
    uncertainty_band: Optional[float] = None
    baseline_origen: str
    tipo_revision: str   # "AUTO" | "MANUAL" | "REVIEW"
    coherence_flag: str  # "OK" | "REVIEW"


class EvaluacionCartaResponse(BaseModel):
    """Respuesta del endpoint de evaluación de carta."""
    mensaje: str
    evaluacion: dict
    preprocesamiento: dict
    calificacion: Optional[ResultadoCalificacionOut] = None