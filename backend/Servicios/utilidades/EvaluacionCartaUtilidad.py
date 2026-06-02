import os
from fastapi import UploadFile

def crear_ruta_almacenamiento_evaluacion_carta(id_evaluacion: int, imagen_frontal: UploadFile, imagen_reversa: UploadFile) -> tuple:
    """Crea la ruta de almacenamiento para las imagenes de evaluación de carta."""

    frontal_ext = os.path.splitext(imagen_frontal.filename or "")[1].lower()
    reversa_ext = os.path.splitext(imagen_reversa.filename or "")[1].lower()

    toma_frontal_path = (
        f"Datos/evaluacion_carta_imagenes/{id_evaluacion}/"
        f"imagen_frontal_{id_evaluacion}{frontal_ext}"
    )
    toma_reversa_path = (
        f"Datos/evaluacion_carta_imagenes/{id_evaluacion}/"
        f"imagen_reversa_{id_evaluacion}{reversa_ext}"
    )

    return toma_frontal_path, toma_reversa_path

def guardar_imagen_evaluacion_carta(imagen: UploadFile, ruta_almacenamiento: str):
    """Guarda la imagen de evaluación de carta en la ruta de almacenamiento especificada (en el filesystem)."""

    os.makedirs(os.path.dirname(ruta_almacenamiento), exist_ok=True)
    imagen.file.seek(0)
    with open(ruta_almacenamiento, "wb") as buffer:
        buffer.write(imagen.file.read())