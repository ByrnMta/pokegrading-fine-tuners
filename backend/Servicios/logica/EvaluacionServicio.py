from sqlalchemy.orm import Session
from fastapi import UploadFile
from Esquemas.EvaluacionCartaEsquema import EvaluacionCartaCreate
from Servicios.validaciones.EvaluacionCartaValidacion import EvaluacionCartaValidacion
from Servicios.utilidades.EvaluacionCartaUtilidad import crear_ruta_almacenamiento_evaluacion_carta
from Servicios.utilidades.EvaluacionCartaUtilidad import guardar_imagen_evaluacion_carta
from AccesoDatos.EvaluacionCartaRepositorio import EvaluacionCartaRepositorio
from Servicios.utilidades.PreprocesarCartaUtilidad import analizar_carta
from AccesoDatos.PreprocesadoCartaRepositorio import PreprocesadoCartaRepositorio


class EvaluacionCartaServicio:

    def registro_evaluacion_carta(db: Session, id_usuario: int, toma_frontal: UploadFile, toma_reversa:UploadFile):
        """Servicio para registrar la evaluación de la carta, que valida los datos recibidos."""

        errores = {}
        try:
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


            ######## AQUÍ SE TENDRÁ QUE LLAMAR AL SERVICIO DE CALIFICACION DE CARTA Y DAR RESPUESTA (se hace en otro archivo dentro de Servicios/logica) #################
            

            return {"mensaje": "Evaluación de carta registrada exitosamente"}
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