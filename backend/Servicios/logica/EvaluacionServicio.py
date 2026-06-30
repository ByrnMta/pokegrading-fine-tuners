from typing import Optional
import hashlib
from sqlalchemy.orm import Session
from fastapi import UploadFile
from Esquemas.EvaluacionCartaEsquema import EvaluacionCartaCreate
from Servicios.validaciones.EvaluacionCartaValidacion import EvaluacionCartaValidacion
from Servicios.utilidades.EvaluacionCartaUtilidad import crear_ruta_almacenamiento_evaluacion_carta
from Servicios.utilidades.EvaluacionCartaUtilidad import guardar_imagen_evaluacion_carta
from AccesoDatos.EvaluacionCartaRepositorio import EvaluacionCartaRepositorio
from Servicios.utilidades.PreprocesarCartaUtilidad import analizar_carta
from AccesoDatos.PreprocesadoCartaRepositorio import PreprocesadoCartaRepositorio
from Servicios.utilidades.CalificarCartaUtilidad import CalificarCartaUtilidad
from AccesoDatos.ResultadoCalificacionRepositorio import ResultadoCalificacionRepositorio


class EvaluacionCartaServicio:

    def registro_evaluacion_carta(
        db: Session,
        id_usuario: int,
        id_sesion: str,
        toma_frontal: UploadFile,
        toma_reversa: UploadFile,
        set_name: Optional[str] = None,
        acabado: Optional[str] = None,
    ):
        """Servicio para registrar la evaluación de la carta, que valida los datos recibidos."""

        errores = {}
        try:
            # Idempotencia combinada: misma sesión Y mismas imágenes.
            # Se calcula la huella y se busca un registro que coincida
            # simultáneamente con ambos criterios.
            repositorio_cal = ResultadoCalificacionRepositorio()
            toma_frontal.file.seek(0)
            frontal_bytes = toma_frontal.file.read()
            toma_reversa.file.seek(0)
            reversa_bytes = toma_reversa.file.read()
            huella_imagenes = hashlib.sha256(frontal_bytes + reversa_bytes).hexdigest()

            # Resetear los punteros para que el resto del flujo pueda leer las imagenes
            toma_frontal.file.seek(0)
            toma_reversa.file.seek(0)

            resultado_existente = repositorio_cal.obtener_por_sesion_y_huella(
                db, id_sesion, huella_imagenes
            )

            if resultado_existente is not None:
                return {
                    "mensaje": "Esta sesion con estas imagenes ya fue procesada.",
                    "evaluacion": {"id": resultado_existente.id_evaluacionCarta,
                                   "estado": resultado_existente.tipo_revision},
                    "calificacion": CalificarCartaUtilidad._mapear_resultado_existente(
                        resultado_existente).get("calificacion"),
                }
            # Validación de la toma frontal 
            EvaluacionCartaValidacion.validar_tamaño_imagen(db, toma_frontal, id_usuario, errores)
            EvaluacionCartaValidacion.validar_formato_imagen(db, toma_frontal, id_usuario, errores)
            EvaluacionCartaValidacion.validar_deteccion_polyglot(db, toma_frontal, id_usuario, errores)

            if errores:
                return {"errores": errores}
            
            # Validación de la toma reversa
            EvaluacionCartaValidacion.validar_tamaño_imagen(db, toma_reversa, id_usuario, errores)
            EvaluacionCartaValidacion.validar_formato_imagen(db, toma_reversa, id_usuario, errores)
            EvaluacionCartaValidacion.validar_deteccion_polyglot(db, toma_reversa, id_usuario, errores)

            if errores:
                return {"errores": errores}

            #validar calidad de imagen de la toma frontal
            EvaluacionCartaValidacion.validar_calidad_imagen(db, toma_frontal, id_usuario, errores)
            #validar calidad de imagen de la toma reversa
            EvaluacionCartaValidacion.validar_calidad_imagen(db, toma_reversa, id_usuario, errores)

            if errores:
                return {"errores": errores}

            # ---------------------------------------- Preprocesamiento de la carta ----------------------------------------

            # Se preprocesa la evaluacion recibida (toma frontal)
            centering_frontal, corners_frontal, edges_frontal, surface_frontal = analizar_carta(toma_frontal, errores)
            # Se valida que en el preprocesamieno no se hayan obtenido errores los resultados del preprocesamiento no sean inválidos (None)
            if errores:
                return {"errores": errores}

            tipo_revision_frontal = "AUTO"
            # Se validan que los resultados del preprocesamiento se hayan podido obtener (No None)
            if centering_frontal is None or corners_frontal is None or edges_frontal is None or surface_frontal is None:
                tipo_revision_frontal = "MANUAL"
            
            # Se preprocesa la evaluacion recibida (toma reversa)
            centering_reversa, corners_reversa, edges_reversa, surface_reversa = analizar_carta(toma_reversa, errores)
            # Se valida que en el preprocesamieno no se hayan obtenido errores los resultados del preprocesamiento no sean inválidos (None)
            if errores:
                return {"errores": errores}

            tipo_revision_reversa = "AUTO"
            # Se validan que los resultados del preprocesamiento se hayan podido obtener (No None)
            if centering_reversa is None or corners_reversa is None or edges_reversa is None or surface_reversa is None:
                tipo_revision_reversa = "MANUAL"
            
            # Se llama a la lógica para crear el registro de evaluación de carta en la base de datos (despues de todas las validaciones y preprocesamientos)
            evaluacion = EvaluacionCartaServicio.logica_crear_evaluacion_carta(db, id_usuario, toma_frontal, toma_reversa)
            
            # Se guardan los resultados del preprocesamiento en la base de datos (toma frontal)
            preprocesado_frontal = PreprocesadoCartaRepositorio.crear_preprocesado_carta(
                db=db, 
                id_evaluacionCarta=evaluacion.id, 
                tipo_revision=tipo_revision_frontal, # puede ser  "AUTO" o "MANUAL" dependiendo de los valores de los scores obtenidos
                centering_score=centering_frontal, 
                corner_score=corners_frontal, 
                edges_score=edges_frontal, 
                surface_score=surface_frontal, 
                tipo_imagen="FRONTAL"
            )

            # Se guardan los resultados del preprocesamiento en la base de datos (toma reversa)
            preprocesado_reversa = PreprocesadoCartaRepositorio.crear_preprocesado_carta(
                db=db,
                id_evaluacionCarta=evaluacion.id,
                tipo_revision=tipo_revision_reversa, # puede ser  "AUTO" o "MANUAL" dependiendo de los valores de los scores obtenidos
                centering_score=centering_reversa,
                corner_score=corners_reversa,
                edges_score=edges_reversa,
                surface_score=surface_reversa,
                tipo_imagen="REVERSA"
            )

            ################ Calificación de carta #######################
            resultado_calificacion = CalificarCartaUtilidad.calificar(
                db=db,
                id_evaluacionCarta=evaluacion.id,
                id_sesion=id_sesion,
                scores_frontal={
                    "centering": centering_frontal,
                    "corners": corners_frontal,
                    "edges": edges_frontal,
                    "surface": surface_frontal,
                },
                scores_reversa={
                    "centering": centering_reversa,
                    "corners": corners_reversa,
                    "edges": edges_reversa,
                    "surface": surface_reversa,
                },
                evaluacion=evaluacion,
                set_name=set_name,
                acabado=acabado,
                huella_imagenes=huella_imagenes,
            )

            return {
                "mensaje": resultado_calificacion.get("mensaje", "Evaluación de carta registrada exitosamente"),
                "evaluacion": {
                    "id": evaluacion.id,
                    "estado": evaluacion.estado,
                    "tipo_revision": resultado_calificacion.get("tipo_revision"),
                    "requiere_accion": resultado_calificacion.get("requiere_accion", False),
                },
                "preprocesamiento": {
                    "frontal": {
                        "centering": centering_frontal,
                        "corners": corners_frontal,
                        "edges": edges_frontal,
                        "surface": surface_frontal,
                        "tipo_revision": tipo_revision_frontal,
                        "tipo_imagen": "FRONTAL",
                    },
                    "reversa": {
                        "centering": centering_reversa,
                        "corners": corners_reversa,
                        "edges": edges_reversa,
                        "surface": surface_reversa,
                        "tipo_revision": tipo_revision_reversa,
                        "tipo_imagen": "REVERSA",
                    },
                },
                "calificacion": resultado_calificacion.get("calificacion"),
            }
        
        except Exception as e:
            db.rollback()
            return {"errores": {"internal": f"Error interno: {str(e)}"}}
        finally:
            db.close()
    
    def logica_crear_evaluacion_carta(db: Session, id_usuario: int, toma_frontal: UploadFile, toma_reversa: UploadFile):
        """Servicio para crear una evaluación de carta"""

        #Se crea primero el registro de evaluación de la carta de un usuario y luego con el id del registro se hace la ruta de almacenamiento de las imágenes
        evaluacion = EvaluacionCartaRepositorio.crear_evaluacion_carta(db, id_usuario, None, None) # esto es al repositorio
        
        #Se crean las rutas de almacenamiento de las imagenes con el id del registro de evaluación
        toma_frontal_path, toma_reversa_path = crear_ruta_almacenamiento_evaluacion_carta(evaluacion.id, toma_frontal, toma_reversa)

        #Se actualizan las rutas de las imágenes en el registro de evaluación de carta
        EvaluacionCartaRepositorio.guardar_ruta_imagen_evaluacion(db, evaluacion, toma_frontal_path, toma_reversa_path)

        #Guardar las imágenes en el filesystem
        guardar_imagen_evaluacion_carta(toma_frontal, toma_frontal_path)
        guardar_imagen_evaluacion_carta(toma_reversa, toma_reversa_path)

        return evaluacion