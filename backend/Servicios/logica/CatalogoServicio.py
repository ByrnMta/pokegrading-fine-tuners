import io
import os
import uuid
from typing import Optional

from fastapi import HTTPException, UploadFile, status
try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    Image = None
    HAS_PIL = False
from sqlalchemy.orm import Session

from AccesoDatos.CartasRepositorio import CartasRepositorio
from Esquemas.CartasEsquema import CartaCreate

# Límites y formatos
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "heic"}
MIN_WIDTH = 200
MIN_HEIGHT = 200



"""
Servicio de catálogo: validaciones y persistencia de cartas.
"""
class CatalogoServicio:
    """Servicio que implementa la lógica para agregar cartas al catálogo."""

    def __init__(self, upload_dir: str = "uploads") -> None:
        """Inicializa repositorio y directorio de uploads."""
        self.repositorio = CartasRepositorio()
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    #============================= Lógica endpoints =============================

    @staticmethod
    def agregar_carta(db: Session, carta_data: CartaCreate, imagen: UploadFile) -> dict:
        """Agrega una carta al catálogo tras validar imagen y duplicados.

        Retorna el registro creado (ORM object compatible con Pydantic).
        """
        # Validaciones de imagen
        CatalogoServicio._validar_imagen(imagen)

        repositorio = CartasRepositorio()
        carta_existente = repositorio.get_carta_by_identidad(db, carta=carta_data)
        if carta_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La carta con la misma combinación de set, número, edición, idioma y acabado ya existe.",
            )

        # Persistir
        ruta_imagen = CatalogoServicio._guardar_imagen(imagen)
        nuevo = repositorio.create_carta(db=db, carta=carta_data, image_path=ruta_imagen)
        return nuevo


    #============================= Validaciones =============================

    @staticmethod
    def _validar_imagen(imagen: UploadFile) -> None:
        """Valida existencia, extensión, tamaño y resolución mínima de la imagen.

        Lanza HTTPException en caso de fallo.
        """
        if not imagen or not getattr(imagen, "filename", None):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se ha subido ninguna imagen.")

        # Tamaño
        imagen.file.seek(0, os.SEEK_END)
        size = imagen.file.tell()
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El tamaño de la imagen no puede exceder los {MAX_FILE_SIZE // (1024 * 1024)} MB.",
            )
        imagen.file.seek(0)

        # Extensión
        extension = imagen.filename.rsplit('.', 1)[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensión de archivo no permitida. Permitidas: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        # Resolución mínima
        if not HAS_PIL:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dependencia 'Pillow' no encontrada en el servidor. Instala las dependencias: pip install -r requirements.txt",
            )

        try:
            contenido = imagen.file.read()
            imagen.file.seek(0)
            with Image.open(io.BytesIO(contenido)) as img:
                width, height = img.size
                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Resolución insuficiente: mínimo {MIN_WIDTH}x{MIN_HEIGHT}px.",
                    )
        except HTTPException:
            raise
        except Exception:
            # Si no se puede abrir la imagen la rechazamos
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo procesar la imagen. Formato o contenido inválido.")


    #============================= Utilidades =============================
    
    @staticmethod
    def _guardar_imagen(imagen: UploadFile) -> str:
        """Guarda imagen en disco y devuelve la ruta relativa.

        Lanza HTTPException si ocurre un error de escritura.
        """
        try:
            extension = imagen.filename.rsplit('.', 1)[-1].lower()
            nombre_archivo = f"{uuid.uuid4()}.{extension}"
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            ruta_archivo = os.path.join(upload_dir, nombre_archivo)

            imagen.file.seek(0)
            with open(ruta_archivo, "wb") as f:
                f.write(imagen.file.read())

            return ruta_archivo
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al guardar la imagen: {e}")
        