from datetime import datetime, timezone
import os
RUTA_LOGS_AUDITORIA = "Datos/Auditoria/auditoria.log"

def agregar_log_evaluacion_carta_fallida(mensaje: str, id_usuario: int):
    """Función para agregar un log de evaluación de carta fallida."""

    carpeta = os.path.dirname(RUTA_LOGS_AUDITORIA)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    linea = f"Fallo de registro de evaluacion de carta [id usuario:{id_usuario}][{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]: {mensaje}\n"
    
    with open(RUTA_LOGS_AUDITORIA, "a", encoding="utf-8") as log_file:
        log_file.write(linea)