from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException
from sqlalchemy.orm import Session
from Servicios.utilidades.GestorCatalogo import CatalogoServicio
from Base_de_Datos.db_session import get_db
from Esquemas.CartasEsquema import Carta as CartaEsquema, CartaCreate

"""Router HTTP para operaciones del catálogo."""

router = APIRouter(prefix="/catalogo", tags=["catalogo"])

@router.post("/carta", response_model=CartaEsquema, status_code=status.HTTP_201_CREATED)
def agregar_carta_al_catalogo(
    numero: str = Form(...),
    set_name: str = Form(...),
    edicion: str = Form(...),
    idioma: str = Form(...),
    acabado: str = Form(...),
    autor: str = Form(...),
    nombre: Optional[str] = Form(None),
    rareza: Optional[str] = Form(None),
    tipo: Optional[str] = Form(None),
    hp: Optional[str] = Form(None),
    ilustrador: Optional[str] = Form(None),
    anio_impresion: Optional[str] = Form(None),
    imagen_frontal: UploadFile = File(...),
    imagen_reverso: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Recibe el formulario de alta y delega toda la lógica al servicio."""
    carta_data = CartaCreate(
        numero=numero,
        set_name=set_name,
        edicion=edicion,
        idioma=idioma,
        acabado=acabado,
        autor=autor,
        nombre=nombre,
        rareza=rareza,
        tipo=tipo,
        hp=hp,
        ilustrador=ilustrador,
        anio_impresion=anio_impresion,
    )
    return CatalogoServicio.agregar_carta(
        db=db,
        carta_data=carta_data,
        imagen_frontal=imagen_frontal,
        imagen_reverso=imagen_reverso,
    )