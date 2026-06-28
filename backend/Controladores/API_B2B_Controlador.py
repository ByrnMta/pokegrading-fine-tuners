from fastapi import APIRouter, Depends, HTTPException, Body, Form
from Datos.db_session import get_db
from sqlalchemy.orm import Session
from Esquemas.CartasEsquema import CartaConsultaB2B
from Servicios.logica.API_B2BServicio import API_B2BServicio
from Servicios.validaciones.API_B2BValidacion import API_B2BValidacion

router = APIRouter(prefix="/B2B", tags=["b2b"])

# ----------------------------------------------------------------------
# Endpoint: consulta de catálogo de cartas por API B2B
# ----------------------------------------------------------------------
@router.post("/consulta-catalogo-b2b", status_code=200)
def buscar_cartas_catalogo_b2b(
        API_key: str = Body(...),
        tienda_id: str = Body(...),
        lista_cartas_consultar: list[dict] = Body(...),
        db: Session = Depends(get_db)
    ):
    
    cartas_consultadas = []
    # Se colocan los datos de las cartas en el formato interno
    for carta in lista_cartas_consultar:
        try:
            carta_b2b = CartaConsultaB2B(
                set_name=carta["set_name"],
                numero=carta["numero"],
                edicion=carta["edicion"],
                idioma=carta["idioma"],
                acabado=carta["acabado"]
            )
            cartas_consultadas.append(carta_b2b)
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Campo obligatorio faltante: {e.args[0]}")

    # Se llama al servicio para hacer la consulta de las cartas en el catálogo
    resultado = API_B2BServicio.consultar_catalogo_b2b(
        db=db, 
        API_key=API_key,
        tienda_id=tienda_id,
        lista_cartas=cartas_consultadas
    )

    if 'errores' in resultado:
        # Si el servicio devuelve errores, se lanza una excepción HTTP con el detalle de los errores
        raise HTTPException(status_code=400, detail=resultado['errores'])
    return resultado

# ----------------------------------------------------------------------
# Endpoint: agregar tienda por API B2B (no fue solicitado)
# ----------------------------------------------------------------------
@router.post("/agregar-tienda-b2b")
def agregar_tienda_b2b(
        API_key: str = Form(...),
        db: Session = Depends(get_db)
    ):
    resultado = API_B2BServicio.agregar_tienda_b2b(
        db=db,
        API_key=API_key
    )
    if 'errores' in resultado:
        raise HTTPException(status_code=400, detail=resultado['errores'])
    return resultado