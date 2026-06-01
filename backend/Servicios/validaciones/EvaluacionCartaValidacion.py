from io import BytesIO

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

class EvaluacionCartaValidacion:

    TAMANO_MAXIMO_IMAGEN = 10 * 1024 * 1024  # 10MB
    EXTENSIONES_PERMITIDAS = {"jpeg", "png", "heic"}

    def validar_tamaño_imagen(db: Session, imagen: UploadFile, errores: dict):
        """Valida que el tamaño de la imagen no exceda los 10MB."""

        # Se valida que el tamaño máximo de la imagen sea 10 MB
        if imagen.size > EvaluacionCartaValidacion.TAMANO_MAXIMO_IMAGEN:
            errores['imagen tamaño'] = "El tamaño de la imagen no debe exceder los 10MB."
            return None
        
    def validar_formato_imagen(db: Session, imagen: UploadFile, errores: dict):
        """Valida que el formato de la imagen sea JPEG, PNG o HEIC."""

        # Se valida que el formato de la imagen sea JPEG, PNG o HEIC
        extension = imagen.filename.split(".")[-1].lower() if "." in imagen.filename else ""
        if extension not in EvaluacionCartaValidacion.EXTENSIONES_PERMITIDAS:
            errores['imagen formato'] = "El formato de la imagen debe ser JPEG, PNG o HEIC."
            return None
    
    def validar_deteccion_polyglot(db: Session, imagen: UploadFile, errores: dict):
        """Valida que la imagen no contenga texto en múltiples idiomas (polyglot)."""

        # Se valida que la imagen no contenga texto en múltiples idiomas (polyglot)
        try:
            imagen.file.seek(0)
            data = imagen.file.read()
        except Exception:
            errores["imagen contenido"] = "No se pudo leer la imagen."
            return None
                
        # Se valida que el archivo no esté vacío
        if not data:
            errores["imagen contenido"] = "La imagen está vacía."
            return None

        # Se valida que el archivo sea una imagen válida
        try:
            Image.open(BytesIO(data)).verify()
        except (UnidentifiedImageError, OSError, ValueError):
            errores["imagen contenido"] = "El archivo no es una imagen valida (corrupto)."
            return None

        # Se valida que la imagen no contenga datos extra luego del fin de la imagen
        try:
            img = Image.open(BytesIO(data))
            img.load()

            if img.fp is not None:
                trailing = img.fp.read()
                if trailing not in (b"", None):
                    errores["imagen contenido"] = "La imagen contiene datos extra."
                    return None
        except (UnidentifiedImageError, OSError, ValueError):
            errores["imagen contenido"] = "El archivo no es una imagen valida."
            return None
        