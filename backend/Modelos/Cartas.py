from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from Datos.db import Base

class Carta(Base):
    __tablename__ = "cartas"

    """ORM model `Carta` que representa la tabla `cartas`.

    Atributos:
    - id: Identificador primario.
    - numero: Número/identificador de la carta dentro del set.
    - set_name: Nombre del set al que pertenece la carta.
    - edicion: Edición o variante del set.
    - idioma: Idioma de la carta.
    - acabado: Acabado/finish de la carta (por ejemplo: holo, non-holo).
    - estado: Estado del flujo de validación (por defecto "PENDIENTE_VALIDACION").
    - image_path: Ruta en disco donde se almacena la imagen asociada.
    - created_at: Marca de tiempo de creación (gestión por la BD).
    """

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), nullable=False)
    set_name = Column(String(100), nullable=False)
    edicion = Column(String(100), nullable=False)
    idioma = Column(String(50), nullable=False)
    acabado = Column(String(50), nullable=False)
    estado = Column(String(50), default="PENDIENTE_VALIDACION")
    image_path = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())