from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from Base_de_Datos.db import Base

class Carta(Base):
    __tablename__ = "cartas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    numero = Column(Integer, nullable=False)
    set_name = Column(String(100), nullable=False)
    image_path = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())