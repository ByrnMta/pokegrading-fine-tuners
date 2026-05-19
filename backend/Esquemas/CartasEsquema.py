from pydantic import BaseModel
from datetime import datetime

class CartaBase(BaseModel):
    nombre: str
    numero: int
    set_name: str

class CartaCreate(CartaBase):
    pass

class Carta(CartaBase):
    id: int
    image_path: str
    created_at: datetime

    class Config:
        from_attributes = True
