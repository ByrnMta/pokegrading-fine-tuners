from sqlalchemy.orm import Session
from Modelos.Pais import Pais

class PaisRepositorio:

    @staticmethod
    def buscar_pais_por_nombre(db: Session, nombre_pais: str) -> Pais | None:
        """Busca un país por su nombre. Retorna el objeto Pais si se encuentra, o None si no se encuentra."""

        pais = db.query(Pais).filter(Pais.nombre == nombre_pais).first()
        if pais:
            return pais # se retorna el objeto Pais si se encuentra el país
        return None
    