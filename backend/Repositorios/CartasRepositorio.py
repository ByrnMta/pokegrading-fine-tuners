from sqlalchemy.orm import Session
from Modelos import Cartas as models
from Esquemas import CartasEsquema as schemas

class CartasRepositorio:
    def get_carta_by_nombre_and_numero(self, db: Session, nombre: str, numero: int):
        # Devuelve una carta por su nombre y número.
        return db.query(models.Carta).filter(models.Carta.nombre == nombre, models.Carta.numero == numero).first()

    def create_carta(self, db: Session, carta: schemas.CartaCreate, image_path: str):
        # Crea una nueva carta en la base de datos.
        db_carta = models.Carta(**carta.dict(), image_path=image_path)
        db.add(db_carta)
        db.commit()
        db.refresh(db_carta)
        return db_carta
