from pydantic import BaseModel
from datetime import datetime

class UsuarioBase(BaseModel):
    id: int
    rol_id: int
    pais_id: int
    idioma_id: int
    nombre_usuario: str
    correo: str
    contrasena: str
    ultimo_acceso: datetime

class UsuarioCreate(UsuarioBase):
    nombre_usuario: str
    correo: str
    contrasena: str
    pais: str
    idioma: str