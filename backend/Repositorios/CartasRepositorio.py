from sqlalchemy.orm import Session
from Modelos import Cartas as models
from Esquemas import CartasEsquema as schemas

class CartasRepositorio:
    def get_carta_by_identidad(self, db: Session, carta: schemas.CartaCreate):
        # Devuelve una carta por su tupla de identidad única.
        return db.query(models.Carta).filter(
            models.Carta.set_name == carta.set_name,
            models.Carta.numero == carta.numero,
            models.Carta.edicion == carta.edicion,
            models.Carta.idioma == carta.idioma,
            models.Carta.acabado == carta.acabado
        ).first()

    def create_carta(self, db: Session, carta: schemas.CartaCreate, image_path: str):
        # Crea una nueva carta en la base de datos.
        db_carta = models.Carta(**carta.dict(), image_path=image_path)
        db.add(db_carta)
        db.commit()
        db.refresh(db_carta)
        return db_carta
