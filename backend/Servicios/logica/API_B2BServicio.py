from sqlalchemy.orm import Session
from Servicios.validaciones.API_B2BValidacion import API_B2BValidacion
from AccesoDatos.API_B2BRepositorio import API_B2BRepositorio
from Esquemas.CartasEsquema import CartaConsultaB2B
from Servicios.utilidades.AuditoriaUtilidad import agregar_log_consulta_catalogo_B2B

class API_B2BServicio:

    @staticmethod    
    def consultar_catalogo_b2b(db: Session, API_key: str, tienda_id: str, lista_cartas: list[CartaConsultaB2B]):
        """Servicio para consultar el catálogo de cartas por API B2B, que valida los datos recibidos."""

        errores = {}
        respuesta = []
        try:
            # Se valida el API key
            tienda = API_B2BValidacion.validar_api_key(db, API_key, errores)
            if errores:
                return {"errores": errores}
            
            # Se valida el identificador propio de la tienda y si se encontró una respuesta cacheada válida
            respuesta_cacheada = API_B2BValidacion.validar_respuesta_cacheada(db, tienda_id)
            if respuesta_cacheada:
                print("Si usó respuesta cacheada")
                return respuesta_cacheada

            # Se valida la lista de cartas recibidas y se obtienen las cartas encontradas en el catálogo
            API_B2BValidacion.validar_lista_cartas(db, lista_cartas, respuesta, errores)
            if errores:
                return {"errores": errores}

            # Se hace un registro de auditoría de la consulta realizada
            agregar_log_consulta_catalogo_B2B(tienda.id)

            respuesta_aux = {"respuesta": respuesta}

            # Se guarda la respuesta como respuesta cacheada para esta tienda
            API_B2BRepositorio.guardar_respuesta_cacheada(db, tienda_id, respuesta_aux)

            return respuesta_aux # se regresa como respuesta la lista de cartas enviada con su respuesta
        except Exception as e:
            db.rollback()
            return {"errores": {"internal": f"Error interno: {str(e)}"}}
        finally:
            db.close()
    
    @staticmethod
    def agregar_tienda_b2b(db: Session, API_key: str):
        """Servicio para agregar una tienda por API B2B."""

        errores = {}
        try:
            # se agrega la tienda B2B con el API key dado
            API_B2BRepositorio.agregar_tienda_b2b(db, API_key)

            return {"respuesta": "Tienda agregada exitosamente"}
        except Exception as e:
            db.rollback()
            return {"errores": {"internal": f"Error interno: {str(e)}"}}
        finally:
            db.close()