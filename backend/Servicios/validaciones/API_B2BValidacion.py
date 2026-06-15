from typing import Optional

from sqlalchemy.orm import Session
from AccesoDatos.API_B2BRepositorio import API_B2BRepositorio
from AccesoDatos.CartasRepositorio import CartasRepositorio


class API_B2BValidacion:

    def validar_api_key(db: Session, API_key: int, errores: dict):
        """Valida que el API key sea válido."""

        # Se busca la tienda con el API key encriptado
        tienda = API_B2BRepositorio.comprobar_api_key(db, API_key)

        # Se valida que se encontró una tienda con el API key proporcionado
        if not tienda:
            errores["API_key"] = "API key inválido. No se encontró ninguna tienda asociada a este API key."
            return None

    def validar_lista_cartas(db: Session, lista_cartas: list[dict], respuesta: list, errores: dict):
        """Valida que la lista de cartas recibida tenga el formato correcto."""

        if lista_cartas is None:
            errores['lista_cartas'] = "No hay cartas proporcionadas."
            return None

        # Se valida que las cartas tengan los atributos necesarios
        for carta in lista_cartas:
            respuesta_carta = API_B2BValidacion.validar_atributos_carta(db, carta, respuesta, errores)
            
            respuesta.append(respuesta_carta)

    def validar_atributos_carta(db: Session, carta: dict, respuesta: list, errores: dict) -> dict | None:
        """Valida que cada carta tenga los atributos necesarios."""
        
        carta_respuesta = {
            "set_name": carta.get("set_name"),
            "numero": carta.get("numero"),
            "edicion": carta.get("edicion"),
            "idioma": carta.get("idioma"),
            "acabado": carta.get("acabado"),
            "estado": "",
            "respuesta": []
        }

        # Se valida si la carta tiene todos los atributos (única coincidencia)
        carta_unica = CartasRepositorio.get_carta_by_identidad(db, carta)
        if carta_unica:
            # Existe una carta exactamente igual con todos los atributos.
            # Se verifica si la carta encontrada está activa
            if carta_unica.estado != "ACTIVA":
                carta_respuesta["estado"] = "no cubierta"
                carta_respuesta["respuesta"] = []
            else:
                carta_respuesta["estado"] = "cubierta"
                carta_respuesta["respuesta"] = [carta] # se coloca la misma carta, dado que son los mismo atributos
                
            return carta_respuesta
            
        # Se buscan la carta con los atributos obligatorios (set_name y numero, coincidencia multiple)
        cartas_coincidentes = CartasRepositorio.get_cartas_by_set_name_and_numero(db, carta.get("set_name"), carta.get("numero"))
        
        if cartas_coincidentes:
            # Se filtran las cartas que tengan los atributos opcionales iguales o nulos (o sea que no importa ese valor)
            cartas_coicidentes_filtradas = API_B2BValidacion.validar_atributos_opcionales(db, carta, cartas_coincidentes, errores)
            
            if not cartas_coicidentes_filtradas:
                # Las cartas existen con los atributos obligatorios, pero no se encontraron coincidencias con los atributos opcionales
                carta_respuesta["estado"] = "paramétros inválidos"
                return carta_respuesta

            # Existen cartas con el mismo set_name y numero, pero no todos los atributos coinciden
            carta_respuesta["estado"] = "coincidencia múltiple"
            carta_respuesta["respuesta"] = cartas_coicidentes_filtradas # se colocan las cartas coincidentes (lista de diccionarios)

            return carta_respuesta
        
        # Si no vienen los atributos obligatorios (set_name y numero), se marca como parámetros inválidos
        carta_respuesta["estado"] = "parámetros inválidos"

        return carta_respuesta
        
    def validar_atributos_opcionales(db: Session, carta: dict, cartas_coincidentes: list, errores: dict) -> dict | None:
        """Valida los atributos opcionales de la carta."""

        lista_cartas_respuesta = []
        # Valida si los atributos opcionales de la carta coinciden con los de las cartas coincidentes
        for carta_coincidente in cartas_coincidentes:
            if (carta.get("edicion") == carta_coincidente.edicion or carta.get("edicion") is None) and \
               (carta.get("idioma") == carta_coincidente.idioma or carta.get("idioma") is None) and \
               (carta.get("acabado") == carta_coincidente.acabado or carta.get("acabado") is None):
                                        
                # Se agrega la carta coincidente con los atributos opcionales que coinciden o son nulos (o sea que no importa ese valor)
                lista_cartas_respuesta.append(carta_coincidente)
        
        return lista_cartas_respuesta # se retorna la lista de cartas que tienen los atributos opcionales iguales o nulos
