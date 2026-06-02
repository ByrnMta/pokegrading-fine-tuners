from sqlalchemy.orm import Session
from Modelos.DominioCorreoInvalido import DominioCorreoInvalido

class CorreosBloqueadosRepositorio:
    """Clase de acceso a la tabla de dominios de correo bloqueados en la base de datos."""

    @staticmethod
    def buscar_dominio_bloqueado(db: Session, dominio: str) -> DominioCorreoInvalido | None:
        """Verifica si un dominio de correo está bloqueado. Retorna None si está bloqueado, o el mismo dominio si no lo está."""

        dominio_bloqueado = db.query(DominioCorreoInvalido).filter(DominioCorreoInvalido.dominio == dominio).first()
        if not dominio_bloqueado:
            return None 
        return dominio # El dominio está bloqueado