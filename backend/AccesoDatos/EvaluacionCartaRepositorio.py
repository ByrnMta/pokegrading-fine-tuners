from sqlalchemy.orm import Session
from Modelos.EvaluacionCarta import EvaluacionCarta

class EvaluacionCartaRepositorio:

    @staticmethod
    def crear_evaluacion_carta(db: Session, id_usuario: int, toma_frontal_path: str, toma_reversa_path: str) -> EvaluacionCarta:
        """Crea una nueva evaluación de carta en la base de datos (la registra)."""

        nueva_evaluacion = EvaluacionCarta(
            id_usuario=id_usuario,
            toma_frontal_path=toma_frontal_path,
            toma_reversa_path=toma_reversa_path
        )
        db.add(nueva_evaluacion)
        db.commit()

        # Se obtiene el registro de la evaluación con su respectivo id generado por la base de datos
        db.refresh(nueva_evaluacion)

        return nueva_evaluacion
    
    @staticmethod
    def guardar_ruta_imagen_evaluacion(db: Session, evaluacion: EvaluacionCarta, toma_frontal_path: str, toma_reversa_path: str) -> EvaluacionCarta:
        """Actualiza las rutas de las imágenes de la evaluación de carta en la base de datos."""

        evaluacion.toma_frontal_path = toma_frontal_path
        evaluacion.toma_reversa_path = toma_reversa_path
        db.commit()
        db.refresh(evaluacion)

        return evaluacion