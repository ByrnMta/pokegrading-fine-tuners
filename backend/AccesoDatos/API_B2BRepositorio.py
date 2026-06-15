from sqlalchemy import Column, Integer, String
from Modelos.TiendaB2B import TiendaB2B
from passlib.context import CryptContext

class API_B2BRepositorio:

    def comprobar_api_key(db, API_key: str):
        """Comprueba la existencia de una tienda B2B asociada al API key proporcionado."""
        
        # Se encripta el API key entrante
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        contrasena = pwd_context.hash(API_key)

        # Se busca la tienda con el API key encriptado
        tienda = db.query(TiendaB2B).filter(TiendaB2B.API_key == contrasena).first()

        return tienda