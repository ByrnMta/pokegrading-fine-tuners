from pydantic import BaseModel
from datetime import datetime

class CartaBase(BaseModel):
    numero: str
    set_name: str
    edicion: str
    idioma: str
    acabado: str

    """Esquema base (Pydantic) con los campos comunes a una carta.

    Se utiliza para validación de entrada y como base para esquemas derivados.
    """

class CartaCreate(CartaBase):
    """Esquema para la creación de una carta.

    Hereda de `CartaBase` y se utiliza en endpoints que reciben datos
    para crear una nueva carta en el catálogo.
    """
    
    pass

class Carta(CartaBase):
    id: int
    estado: str
    image_path: str
    created_at: datetime

    class Config:
        from_attributes = True
    
    """Esquema que representa una carta completa devuelta por la API.

    Contiene los campos de `CartaBase` más metadata gestionada por el sistema
    (`id`, `estado`, `image_path`, `created_at`).
    """
