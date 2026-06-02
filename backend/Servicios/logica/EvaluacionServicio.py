from sqlalchemy.orm import Session
from fastapi import UploadFile
from Esquemas.EvaluacionCartaEsquema import EvaluacionCartaCreate
from Servicios.validaciones.EvaluacionCartaValidacion import EvaluacionCartaValidacion
from Servicios.utilidades.EvaluacionCartaUtilidad import crear_ruta_almacenamiento_evaluacion_carta
from Servicios.utilidades.EvaluacionCartaUtilidad import guardar_imagen_evaluacion_carta
from AccesoDatos.EvaluacionCartaRepositorio import EvaluacionCartaRepositorio


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

            #validar calidad de imagen de la toma frontal
            EvaluacionCartaValidacion.validar_calidad_imagen(db, toma_frontal, errores)
            #validar calidad de imagen de la toma reversa
            EvaluacionCartaValidacion.validar_calidad_imagen(db, toma_reversa, errores)

            if errores:
                return {"errores": errores}

            #Se crea primero el registro de evaluación de la carta de un usuario y luego con el id del registro, se hace la ruta de almacenamiento de las imágenes
            evaluacion = EvaluacionCartaRepositorio.crear_evaluacion_carta(db, id_usuario, None, None)
            
            #Se crean las rutas de almacenamiento de las imagenes con el id del registro de evaluación
            toma_frontal_path, toma_reversa_path = crear_ruta_almacenamiento_evaluacion_carta(evaluacion.id, toma_frontal, toma_reversa)

            #Se actualizan las rutas de las imágenes en el registro de evaluación de carta
            EvaluacionCartaRepositorio.guardar_ruta_imagen_evaluacion(db, evaluacion, toma_frontal_path, toma_reversa_path)

            #Guardar las imágenes en el filesystem
            guardar_imagen_evaluacion_carta(toma_frontal, toma_frontal_path)
            guardar_imagen_evaluacion_carta(toma_reversa, toma_reversa_path)

            return {"mensaje": "Evaluación de carta registrada exitosamente"}

        except Exception as e:
            db.rollback()
            return {"errores": {"internal": f"Error interno: {str(e)}"}}
        finally:
            db.close()