from sqlalchemy import Column, Integer, String
from Datos.db import Base

class TiendaB2B(Base):
    __tablename__ = "tienda_b2b"

    """Tabla para almacenar la información de las tiendas B2B que pueden acceder a la API."""

    id = Column(Integer, primary_key=True, index=True)
    API_key = Column(String(60), unique=True, index=True, nullable=False)
    estado = Column(String(20), default="ACTIVO", nullable=False)
