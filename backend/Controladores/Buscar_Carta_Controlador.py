from typing import Optional

import os

from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException
from sqlalchemy.orm import Session

from Datos.db_session import get_db
from Servicios.logica.Grading_Submitter import Submitter

"""Router HTTP para operaciones del submitter."""

router = APIRouter(prefix="/submitter", tags=["submitter"])

@router.post("/buscar", status_code=status.HTTP_200_OK)
def buscar_carta_por_imagen(
    imagen_frontal: UploadFile = File(...),
    imagen_reverso: Optional[UploadFile] = File(None),
    top_k: int = Form(3),
    db: Session = Depends(get_db),
):
    """Busca las cartas más similares a la imagen proporcionada y devuelve top-K candidatos."""
    try:
        submitter = Submitter(catalogo_dir=os.path.join("Datos", "catalogo"))
        resultado = submitter.buscar_imagenes(
            db=db,
            imagen_frontal=imagen_frontal,
            imagen_reverso=imagen_reverso,
            top_k=top_k,
        )
        return {"candidatos": resultado.candidatos, "evaluacion": resultado.evaluacion}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

