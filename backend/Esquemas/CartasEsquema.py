from pydantic import BaseModel
from datetime import datetime
from typing import Optional

"""Esquemas Pydantic para lectura y escritura de cartas.

Separan la forma en que el catálogo recibe datos de la forma en que los expone
en la respuesta, manteniendo claro qué campos son obligatorios y cuáles son
recomendados.
"""

class CartaBase(BaseModel):
    """Campos de identidad que definen una carta de forma única."""

    numero: str
    set_name: str
    edicion: str
    idioma: str
    acabado: str

class CartaDisplay(BaseModel):
    """Campos opcionales usados para enriquecer la visualización de la carta."""

    nombre: Optional[str] = None
    rareza: Optional[str] = None
    tipo: Optional[str] = None
    hp: Optional[int] = None
    ilustrador: Optional[str] = None
    anio_impresion: Optional[int] = None

    """Campos de display recomendados para una carta."""


class CartaCreate(CartaBase):
    """Payload de creación para el alta de una carta en el catálogo."""

    autor: str
    nombre: Optional[str] = None
    rareza: Optional[str] = None
    tipo: Optional[str] = None
    hp: Optional[str] = None
    ilustrador: Optional[str] = None
    anio_impresion: Optional[str] = None

class Carta(CartaBase, CartaDisplay):
    """Representación completa de una carta devuelta por la API."""

    id: int
    card_id: str
    autor: str
    estado: str
    image_front_path: str
    image_back_path: str
    created_at: datetime

    class Config:
        from_attributes = True
