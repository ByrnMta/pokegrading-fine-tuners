from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from Servicios.CatalogoServicio import CatalogoServicio
from Base_de_Datos.db_session import get_db
from Esquemas.CartasEsquema import Carta as CartaEsquema

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
)

servicio_catalogo = CatalogoServicio()

@router.post("/cards", response_model=CartaEsquema, status_code=status.HTTP_201_CREATED)
def agregar_carta_al_catalogo(
    nombre: str = Form(...),
    numero: int = Form(...),
    set_name: str = Form(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Endpoint para agregar una nueva carta al catálogo.
    return servicio_catalogo.agregar_carta(
        db=db,
        nombre=nombre,
        numero=numero,
        set_name=set_name,
        imagen=imagen
    )
