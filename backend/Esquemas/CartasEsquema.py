from pydantic import BaseModel
from datetime import datetime

class CartaBase(BaseModel):
    numero: int
    set_name: str
    edicion: str
    idioma: str
    acabado: str

class CartaCreate(CartaBase):
    pass

class Carta(CartaBase):
    id: int
    estado: str
    image_path: str
    created_at: datetime

    class Config:
        orm_mode = True
