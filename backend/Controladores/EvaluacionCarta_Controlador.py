from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from Base_de_Datos.db_session import get_db
from sqlalchemy.orm import Session
from Servicios.logica.EvaluacionServicio import EvaluacionCartaServicio


router = APIRouter(prefix="/evaluacion-carta", tags=["evaluacion-carta"])

# ----------------------------------------------------------------------
# Endpoint: enviar evaluación de carta
# ----------------------------------------------------------------------
@router.post("/enviar-evaluacion")
def enviar_evaluacion_carta(
        id_usuario: int,
        toma_frontal: UploadFile = File(...),
        toma_reversa: UploadFile = File(...),
        db: Session = Depends(get_db)
    ):
    
    # Se llama al servicio para registrar la evaluación de la carta (se hace de forma directa dado que hay archivos involucrados)
    resultado = EvaluacionCartaServicio.registro_evaluacion_carta(
        db=db, 
        id_usuario=id_usuario, 
        toma_frontal=toma_frontal, 
        toma_reversa=toma_reversa
    )
    
    if 'errores' in resultado:
        # Si el servicio devuelve errores, se lanza una excepción HTTP con el detalle de los errores
        raise HTTPException(status_code=400, detail=resultado['errores'])

    return resultado