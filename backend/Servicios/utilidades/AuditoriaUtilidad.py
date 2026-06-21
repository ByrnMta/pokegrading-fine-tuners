from datetime import datetime, timezone
import os
RUTA_LOGS_AUDITORIA_EVALUACION_CARTA = "Datos/Auditoria/auditoria_evaluacion_carta.log"
RUTA_LOGS_AUDITORIA_CONSULTA_B2B = "Datos/Auditoria/auditoria_b2b.log"

def agregar_log_evaluacion_carta_fallida(mensaje: str, id_usuario: int):
    """Función para agregar un log de evaluación de carta fallida."""

    carpeta = os.path.dirname(RUTA_LOGS_AUDITORIA_EVALUACION_CARTA)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    linea = f"Fallo de registro de evaluacion de carta [id usuario:{id_usuario}][{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]: {mensaje}\n"
    
    with open(RUTA_LOGS_AUDITORIA_EVALUACION_CARTA, "a", encoding="utf-8") as log_file:
        log_file.write(linea)

def agregar_log_consulta_catalogo_B2B(API_key_id: int):
    """Función para agregar un log de consulta de catálogo por API B2B."""

    carpeta = os.path.dirname(RUTA_LOGS_AUDITORIA_CONSULTA_B2B)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    linea = f"Consulta de catálogo por API B2B [id tienda:{API_key_id}][{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]\n"
    
    with open(RUTA_LOGS_AUDITORIA_CONSULTA_B2B, "a", encoding="utf-8") as log_file:
        log_file.write(linea)