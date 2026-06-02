from sqlalchemy.orm import Session
from Modelos.Idioma import Idioma

class IdiomaRepositorio:

    @staticmethod
    def buscar_idioma_por_nombre(db: Session, nombre_idioma: str) -> Idioma | None:
        """Busca un idioma por su nombre. Retorna el objeto Idioma si se encuentra, o None si no se encuentra."""

        idioma = db.query(Idioma).filter(Idioma.nombre == nombre_idioma).first()
        if idioma:
            return idioma # se retorna el objeto Idioma si se encuentra el idioma
        return None