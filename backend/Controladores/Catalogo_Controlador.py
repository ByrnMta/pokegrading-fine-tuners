from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from Servicios.CatalogoServicio import CatalogoServicio
from Base_de_Datos.db_session import get_db
from Esquemas.CartasEsquema import Carta as CartaEsquema, CartaCreate

router = APIRouter(prefix="/catalogo", tags=["catalogo"])

@router.post("/carta", response_model=CartaEsquema, status_code=status.HTTP_201_CREATED)
def agregar_carta_al_catalogo(
        numero: str = Form(...),
        set_name: str = Form(...),
        edicion: str = Form(...),
        idioma: str = Form(...),
        acabado: str = Form(...),
        imagen: UploadFile = File(...),
        db: Session = Depends(get_db)
    ):
    """Endpoint: agrega una nueva carta al catálogo.

    Parámetros recibidos por `Form`/`File`:
    - `numero`, `set_name`, `edicion`, `idioma`, `acabado`: campos de la carta.
    - `imagen`: archivo cargado con la imagen de la carta.
    - `db`: sesión de base de datos inyectada por dependencia.

    Valida y persiste la carta delegando en `CatalogoServicio.agregar_carta`.
    Devuelve el registro creado usando el esquema de respuesta `Carta`.
    """
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
