from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from Datos.db_session import get_db
from sqlalchemy.orm import Session
from Servicios.logica.EvaluacionServicio import EvaluacionCartaServicio


router = APIRouter(prefix="/evaluacion-carta", tags=["evaluacion-carta"])

# ----------------------------------------------------------------------
# Endpoint: enviar evaluacion de carta
# ----------------------------------------------------------------------
@router.post("/enviar-evaluacion", status_code=201)
def enviar_evaluacion_carta(
        id_usuario: int = Form(...),
        id_sesion: str = Form(...),
        toma_frontal: UploadFile = File(...),
        toma_reversa: UploadFile = File(...),
        set_name: Optional[str] = Form(None),
        acabado: Optional[str] = Form(None),
        db: Session = Depends(get_db)
    ):

    # Se llama al servicio para registrar la evaluacion de la carta
    resultado = EvaluacionCartaServicio.registro_evaluacion_carta(
        db=db,
        id_usuario=id_usuario,
        id_sesion=id_sesion,
        toma_frontal=toma_frontal,
        toma_reversa=toma_reversa,
        set_name=set_name,
        acabado=acabado,
    )

    if 'errores' in resultado:
        # Si el servicio devuelve errores, se lanza una excepción HTTP con el detalle de los errores
        status_code = resultado['errores'].get('status_code', 400)
        raise HTTPException(status_code=status_code, detail=resultado['errores'])

    return resultado