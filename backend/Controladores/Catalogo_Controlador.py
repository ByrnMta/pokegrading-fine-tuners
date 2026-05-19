from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from Base_de_Datos.db_session import get_db
from Servicios.CatalogoServicio import CatalogoServicio
from Esquemas.CartasEsquema import Carta as CartaEsquema

router = APIRouter(prefix="/catalogo", tags=["catalogo"])

# ----------------------------------------------------------------------
# Endpoint: agregar nueva carta al catálogo
# ----------------------------------------------------------------------
@router.post("/cartas", response_model=CartaEsquema, status_code=status.HTTP_201_CREATED)
def agregar_carta_al_catalogo(
        nombre: str = Form(...),
        numero: int = Form(...),
        set_name: str = Form(...),
        imagen: UploadFile = File(...),
        db: Session = Depends(get_db)
    ):
    resultado = CatalogoServicio.agregar_carta(
        db=db,
        nombre=nombre,
        numero=numero,
        set_name=set_name,
        imagen=imagen
    )
    return resultado
