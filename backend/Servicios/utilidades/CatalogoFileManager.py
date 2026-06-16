import os
import uuid
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile, status

"""Manejador de archivos para el catálogo de cartas.

Este módulo se encarga de todas las operaciones relacionadas con archivos
y directorios para el catálogo de cartas.
"""

DATA_ROOT = os.path.join("Datos", "catalogo")

class CatalogoFileManager:
    """Clase con métodos estáticos para manejo de archivos del catálogo."""
    
    @staticmethod
    def generar_card_id() -> str:
        """Genera un identificador interno único e inmutable para la carta."""
        return str(uuid.uuid4())
    
    @staticmethod
    def crear_directorio_carta(card_id: str) -> str:
        """Crea la carpeta Datos/catalogo/card_id con subdirectorios images y embeds."""
        card_dir = os.path.join(DATA_ROOT, card_id)
        os.makedirs(card_dir, exist_ok=True)
        os.makedirs(os.path.join(card_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(card_dir, "embeds"), exist_ok=True)
        return card_dir
    
    @staticmethod
    def obtener_extension(nombre_archivo: str) -> Optional[str]:
        """Retorna la extensión normalizada del archivo o None si no existe."""
        if "." not in nombre_archivo:
            return None
        return nombre_archivo.rsplit(".", 1)[-1].lower()
    
    @staticmethod
    def guardar_imagenes(
        card_id: str,
        imagen_frontal: UploadFile,
        imagen_reverso: UploadFile,
    ) -> Tuple[str, str]:
        """Guarda ambas imágenes y revierte la primera si la segunda falla."""
        card_dir = CatalogoFileManager.crear_directorio_carta(card_id)
        
        try:
            ruta_frontal = CatalogoFileManager._guardar_imagen_unica(
                card_id, "front", imagen_frontal, card_dir
            )
            ruta_reverso = CatalogoFileManager._guardar_imagen_unica(
                card_id, "back", imagen_reverso, card_dir
            )
            return ruta_frontal, ruta_reverso
        except Exception as e:
            # Si ocurre un error, intentar limpiar cualquier archivo creado
            CatalogoFileManager.borrar_archivo(ruta_frontal if 'ruta_frontal' in locals() else None)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar las imágenes: {e}",
            )
    
    @staticmethod
    def _guardar_imagen_unica(
        card_id: str,
        sufijo: str,
        imagen: UploadFile,
        card_dir: str
    ) -> str:
        """Persiste una imagen en disco usando el card_id como prefijo."""
        try:
            extension = CatalogoFileManager.obtener_extension(imagen.filename)
            if not extension:
                raise ValueError("Nombre de archivo sin extensión")
            
            nombre_archivo = f"{sufijo}.{extension}"
            images_dir = os.path.join(card_dir, "images")
            os.makedirs(images_dir, exist_ok=True)
            ruta_archivo = os.path.join(images_dir, nombre_archivo)

            imagen.file.seek(0)
            with open(ruta_archivo, "wb") as f:
                f.write(imagen.file.read())
            return ruta_archivo
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar la imagen: {e}",
            )
    
    @staticmethod
    def borrar_archivo(ruta_archivo: Optional[str]) -> None:
        """Elimina un archivo si existe, ignorando errores de limpieza."""
        if not ruta_archivo:
            return
        try:
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
        except Exception:
            return
    
    @staticmethod
    def borrar_directorio_carta(ruta_directorio: Optional[str]) -> None:
        """Elimina la carpeta de la carta completa si existe."""
        if not ruta_directorio:
            return
        try:
            if os.path.isdir(ruta_directorio):
                for root, dirs, files in os.walk(ruta_directorio, topdown=False):
                    for file_name in files:
                        try:
                            os.remove(os.path.join(root, file_name))
                        except Exception:
                            pass
                    for dir_name in dirs:
                        try:
                            os.rmdir(os.path.join(root, dir_name))
                        except Exception:
                            pass
                os.rmdir(ruta_directorio)
        except Exception:
            return
    
    @staticmethod
    def obtener_ruta_embeddings(card_dir: str) -> str:
        """Retorna la ruta completa para el directorio de embeddings."""
        return os.path.join(card_dir, "embeds")
    
    @staticmethod
    def obtener_ruta_imagenes(card_dir: str) -> str:
        """Retorna la ruta completa para el directorio de imágenes."""
        return os.path.join(card_dir, "images")