from pydantic import BaseModel
from datetime import datetime

class UsuarioBase(BaseModel):
    """Esquema base para la representación de un usuario en internamente."""

    id: int
    rol_id: int
    pais_id: int
    idioma_id: int
    nombre_usuario: str
    correo: str
    contrasena: str
    ultimo_acceso: datetime

class UsuarioCreate(BaseModel):
    """Esquema para la creación de un nuevo usuario, con los campos necesarios para el registro."""

    nombre_usuario: str
    correo: str
    contrasena: str
    pais: str
    idioma: str