from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from Datos.db_session import get_db
from sqlalchemy.orm import Session
from Esquemas.CartasEsquema import CartaConsultaB2B
from Servicios.logica.API_B2BServicio import API_B2BServicio

router = APIRouter(prefix="/B2B", tags=["b2b"])

# ----------------------------------------------------------------------
# Endpoint: consulta de catálogo de cartas por API B2B
# ----------------------------------------------------------------------
@router.post("/consulta-catalogo-b2b")
def buscar_cartas_catalogo_b2b(
        API_key: int = Form(...),
        lista_cartas_consultar: list[dict] = Form(...),
        db: Session = Depends(get_db)
    ):

    cartas_consultadas = []

    # Se colocan los datos de las cartas en el formato interno
    for carta in lista_cartas_consultar:
        carta_b2b = CartaConsultaB2B(
            set_name=carta.get("set_name"),
            numero=carta.get("numero"),
            edicion=carta.get("edicion"),
            idioma=carta.get("idioma"),
            acabado=carta.get("acabado")
        )
        cartas_consultadas.append(carta_b2b)
    
    # Se llama al servicio para hacer la consulta de las cartas en el catálogo
    resultado = API_B2BServicio.consultar_catalogo_b2b(
        db=db, 
        API_key=API_key, 
        lista_cartas=cartas_consultadas
    )

    if 'errores' in resultado:
        # Si el servicio devuelve errores, se lanza una excepción HTTP con el detalle de los errores
        raise HTTPException(status_code=400, detail=resultado['errores'])
    return resultado