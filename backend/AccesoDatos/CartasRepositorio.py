from sqlalchemy.orm import Session
from Modelos import Cartas as models

"""Acceso a datos para la entidad Carta.

Este repositorio encapsula consultas y escritura de cartas para evitar que la
lógica de negocio opere directamente sobre el ORM.
"""

class CartasRepositorio:
    """Operaciones de persistencia asociadas a cartas."""

    def get_carta_by_identidad(self, db: Session, identidad: dict):
        """Busca una carta por la combinación que define su identidad única."""
        return db.query(models.Carta).filter(
            models.Carta.set_name == identidad["set_name"],
            models.Carta.numero == identidad["numero"],
            models.Carta.edicion == identidad["edicion"],
            models.Carta.idioma == identidad["idioma"],
            models.Carta.acabado == identidad["acabado"],
        ).first()

    def create_carta(
        self,
        db: Session,
        carta_data: dict,
        card_id: str,
        image_front_path: str,
        image_back_path: str,
        estado: str,
    ):
        """Crea una carta nueva y deja la transacción abierta para el servicio."""
        db_carta = models.Carta(
            card_id=card_id,
            numero=carta_data["numero"],
            set_name=carta_data["set_name"],
            edicion=carta_data["edicion"],
            idioma=carta_data["idioma"],
            acabado=carta_data["acabado"],
            nombre=carta_data.get("nombre"),
            rareza=carta_data.get("rareza"),
            tipo=carta_data.get("tipo"),
            hp=carta_data.get("hp"),
            ilustrador=carta_data.get("ilustrador"),
            anio_impresion=carta_data.get("anio_impresion"),
            autor=carta_data["autor"],
            estado=estado,
            image_front_path=image_front_path,
            image_back_path=image_back_path,
        )
        db.add(db_carta)
        db.flush()
        return db_carta

    def get_all_cartas(self, db: Session):
        """Retorna todas las cartas (entidades ORM)."""
        return db.query(models.Carta).all()
    
    def get_cartas_by_set_name_and_numero(self, db: Session, set_name: str, numero: str) -> list[dict] | None:
        """Busca cartas por set_name y numero, siempre y cuando estén activas."""
        
        # Se buscan las cartas con el set_name y numero proporcionados (todas las posibles coincidencias), se obtiene una lista de cartas
        cartas = db.query(models.Carta).filter(
            models.Carta.set_name == set_name,
            models.Carta.numero == numero,
            models.Carta.estado == "ACTIVA"
        ).all()

        # Se ajusta el formato de las cartas
        cartas_respuesa = [self.cartaModel_to_cartaBase(carta) for carta in cartas]

        return cartas_respuesa  # lo que se retorna es una lista de cartas

    def cartaModel_to_cartaBase(self, carta_model: models.Carta) -> dict:
        """Convierte un modelo de carta a un diccionario con los campos de CartaBase."""
        return {
            "set_name": carta_model.set_name,
            "numero": carta_model.numero,
            "edicion": carta_model.edicion,
            "idioma": carta_model.idioma,
            "acabado": carta_model.acabado
        }
    