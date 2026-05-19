from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from Servicios.CatalogoServicio import CatalogoServicio
from Base_de_Datos.db_session import get_db
from Esquemas.CartasEsquema import Carta as CartaEsquema, CartaCreate

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.post("/cards", response_model=CartaEsquema, status_code=status.HTTP_201_CREATED)
def agregar_carta_al_catalogo(
        numero: str = Form(...),
        set_name: str = Form(...),
        edicion: str = Form(...),
        idioma: str = Form(...),
        acabado: str = Form(...),
        imagen: UploadFile = File(...),
        db: Session = Depends(get_db)
    ):
    # Endpoint para agregar una nueva carta al catálogo.
    carta_data = CartaCreate(
        numero=numero,
        set_name=set_name,
        edicion=edicion,
        idioma=idioma,
        acabado=acabado
    )
    return CatalogoServicio.agregar_carta(
        db=db,
        carta_data=carta_data,
        imagen=imagen
    )
