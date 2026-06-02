from datetime import datetime, timezone

RUTA_LOGS_AUDITORIA = "Datos/Auditoria/auditoria.log"

def agregar_log_evaluacion_carta_fallida(mensaje: str, id_usuario: int):
    """Función para agregar un log de evaluación de carta fallida."""
    with open(RUTA_LOGS_AUDITORIA, "a") as log_file:
        log_file.write(f"Fallo de registro de evaluacion de carta [id usuario:{id_usuario}][{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}]: {mensaje}\n")

    