from sqlalchemy.orm import Session
from fastapi import UploadFile
from Esquemas.EvaluacionCartaEsquema import EvaluacionCartaCreate
from Servicios.validaciones.EvaluacionCartaValidacion import EvaluacionCartaValidacion


class EvaluacionCartaServicio:

    def registro_evaluacion_carta(db: Session, id_usuario: int, toma_frontal: UploadFile, toma_reversa:UploadFile):
        """Servicio para registrar la evaluación de la carta, que valida los datos recibidos."""

        errores = {}
        try:
            # Validación de la toma frontal 
            EvaluacionCartaValidacion.validar_tamaño_imagen(db, toma_frontal, errores)
            EvaluacionCartaValidacion.validar_formato_imagen(db, toma_frontal, errores)
            EvaluacionCartaValidacion.validar_deteccion_polyglot(db, toma_frontal, errores)

            if errores:
                return {"errores": errores}
            
            # Validación de la toma reversa
            EvaluacionCartaValidacion.validar_tamaño_imagen(db, toma_reversa, errores)
            EvaluacionCartaValidacion.validar_formato_imagen(db, toma_reversa, errores)
            EvaluacionCartaValidacion.validar_deteccion_polyglot(db, toma_reversa, errores)

            if errores:
                return {"errores": errores}
            
            return {"mensaje": "Evaluación de carta registrada exitosamente"}

        except Exception as e:
            db.rollback()
            return {"errores": {"internal": f"Error interno: {str(e)}"}}
        finally:
            db.close()