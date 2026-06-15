from sqlalchemy.orm import Session
from Servicios.validaciones.API_B2BValidacion import API_B2BValidacion

class API_B2BServicio:

    def consultar_catalogo_b2b(db: Session, API_key: int, lista_cartas: list[dict]):
        """Servicio para consultar el catálogo de cartas por API B2B, que valida los datos recibidos."""

        errores = {}
        respuesta = []
        try:
            # Se valida el API key
            API_B2BValidacion.validar_api_key(db, API_key, errores)
            if errores:
                return {"errores": errores}

            # Se valida la lista de cartas recibidas y se obtienen las cartas encontradas en el catálogo
            respuesta = API_B2BValidacion.validar_lista_cartas(db, lista_cartas, respuesta, errores)
            if errores:
                return {"errores": errores}

            return {"respuesta": respuesta} # se regresa como respuesta la lista de cartas enviada con su respuesta
        except Exception as e:
            db.rollback()
            return {"errores": {"internal": f"Error interno: {str(e)}"}}
        finally:
            db.close()