from sqlalchemy import Column, Integer, String
from Modelos.TiendaB2B import TiendaB2B
from Servicios.utilidades.API_B2BUtilidad import hashing_api_key
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from Modelos.RespuestaCacheadaB2B import RespuestaCacheada

class API_B2BRepositorio:

    def obtener_tiendas_B2B(db):
        """Obtiene todas las tiendas B2B."""
        tiendas = db.query(TiendaB2B).all()

        return tiendas
    
    def agregar_tienda_b2b(db, API_key: str):
        """Agrega una nueva tienda B2B al sistema con el API key proporcionado."""

        # Se encripta el API key
        contrasena = hashing_api_key(API_key)

        # Se crea una nueva instancia de TiendaB2B
        nueva_tienda = TiendaB2B(API_key=contrasena)

        # Se agrega la nueva tienda a la base de datos
        db.add(nueva_tienda)
        db.commit()
        db.refresh(nueva_tienda) # actualiza el objeto con el id generado por la base de datos

        return nueva_tienda
    
    def obtener_respuesta_cacheada(db, tienda_id: str) -> RespuestaCacheada | None:
        """Obtiene la respuesta cacheada para una tienda específica, a partir de su identifacador propio."""

        respuesta = db.query(RespuestaCacheada).filter(RespuestaCacheada.tienda_id == tienda_id).first()
        return respuesta
    
    def guardar_respuesta_cacheada(db, tienda_id: str, respuesta_body: dict):
        """Guarda una nueva respuesta en la caché."""

        # Asegurarse de que el cuerpo de la respuesta sea JSON-serializable
        payload = jsonable_encoder(respuesta_body)

        # Evitar error UNIQUE: si ya existe una entrada para la misma tienda_id, actualizarla
        existente = db.query(RespuestaCacheada).filter(RespuestaCacheada.tienda_id == tienda_id).first()
        if existente:
            existente.respuesta_body = payload
            existente.fecha_creacion = datetime.utcnow()
            db.add(existente)
            db.commit()
            db.refresh(existente)
            return existente

        # Si no existe una entrada previa, crear una nueva
        db_response = RespuestaCacheada(
            tienda_id=tienda_id,
            respuesta_body=payload
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response
    