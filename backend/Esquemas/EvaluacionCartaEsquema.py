from pydantic import BaseModel
from datetime import datetime

class EvaluacionCartaBase(BaseModel):
    """Esquema base para la representación de una evaluación de carta internamente."""

    id: int
    id_usuario: int
    toma_frontal_path: str
    toma_reversa_path: str
    fecha_evaluacion: datetime

class EvaluacionCartaCreate(BaseModel):
    """Esquema para la creación de una nueva evaluación de carta, con los campos necesarios para el registro."""

    id_usuario: int
    toma_frontal_path: str
    toma_reversa_path: str