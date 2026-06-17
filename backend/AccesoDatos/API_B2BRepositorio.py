from sqlalchemy import Column, Integer, String
from Modelos.TiendaB2B import TiendaB2B
from Servicios.utilidades.API_B2BUtilidad import hashing_api_key

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
    