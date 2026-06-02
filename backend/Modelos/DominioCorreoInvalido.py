from sqlalchemy import Column, Integer, String
from Datos.db import Base

class DominioCorreoInvalido(Base):
    """Modelo ORM para representar dominios de correo bloqueados en la base de datos."""

    __tablename__ = "dominio_correo_invalido"
    
    id = Column(Integer, primary_key=True)
    dominio = Column(String(100), unique=True, nullable=False)
