import os
import uuid
from typing import Optional, Tuple, List, Dict
from fastapi import HTTPException, UploadFile, status

try:
    import numpy as np
except Exception:
    np = None

"""Repositorio para operaciones de archivos del catálogo.

Este módulo centraliza todas las operaciones de archivos y directorios
relacionados con el catálogo de cartas, incluyendo imágenes y embeddings.
"""

DATA_ROOT = os.path.join("Datos", "catalogo")


class ArchivosRepositorio:
    """Clase con métodos estáticos para operaciones de archivos del catálogo."""
    
    @staticmethod
    def generar_card_id() -> str:
        """Genera un identificador interno único e inmutable para la carta."""
        return str(uuid.uuid4())
    
    @staticmethod
    def crear_directorio_carta(card_id: str, catalogo_dir: str = DATA_ROOT) -> str:
        """Crea la carpeta catalogo_dir/card_id con subdirectorios images y embeds."""
        card_dir = os.path.join(catalogo_dir, card_id)
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
        catalogo_dir: str = DATA_ROOT,
    ) -> Tuple[str, str]:
        """Guarda ambas imágenes y revierte la primera si la segunda falla."""
        card_dir = ArchivosRepositorio.crear_directorio_carta(card_id, catalogo_dir)
        
        try:
            ruta_frontal = ArchivosRepositorio._guardar_imagen_unica(
                card_id, "front", imagen_frontal, card_dir
            )
            ruta_reverso = ArchivosRepositorio._guardar_imagen_unica(
                card_id, "back", imagen_reverso, card_dir
            )
            return ruta_frontal, ruta_reverso
        except Exception as e:
            # Si ocurre un error, intentar limpiar cualquier archivo creado
            ArchivosRepositorio.borrar_archivo(ruta_frontal if 'ruta_frontal' in locals() else None)
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
            extension = ArchivosRepositorio.obtener_extension(imagen.filename)
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
    def leer_imagen(ruta_imagen: str) -> bytes:
        """Lee una imagen del disco y retorna sus bytes."""
        try:
            with open(ruta_imagen, "rb") as f:
                return f.read()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al leer la imagen: {e}",
            )
    
    @staticmethod
    def guardar_embedding(
        card_id: str,
        sufijo: str,
        embedding,
        catalogo_dir: str = DATA_ROOT,
    ) -> str:
        """Persiste un embedding como archivo .npy."""
        if np is None:
            raise RuntimeError("NumPy es requerido para operaciones con embeddings")
        
        try:
            card_dir = os.path.join(catalogo_dir, card_id)
            embeds_dir = os.path.join(card_dir, "embeds")
            os.makedirs(embeds_dir, exist_ok=True)
            
            nombre_archivo = f"{sufijo}.npy"
            ruta_embedding = os.path.join(embeds_dir, nombre_archivo)
            
            np.save(ruta_embedding, embedding)
            return ruta_embedding
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar el embedding: {e}",
            )
    
    @staticmethod
    def leer_embedding(ruta_embedding: str):
        """Lee un embedding desde disco."""
        if np is None:
            raise RuntimeError("NumPy es requerido para operaciones con embeddings")
        
        try:
            return np.load(ruta_embedding)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al leer el embedding: {e}",
            )
    
    @staticmethod
    def listar_embeddings(catalogo_dir: str = DATA_ROOT) -> List[Dict]:
        """Lista todos los embeddings disponibles en el catálogo."""
        resultados = []
        
        if not os.path.exists(catalogo_dir):
            return resultados
        
        for card_folder in os.listdir(catalogo_dir):
            card_dir = os.path.join(catalogo_dir, card_folder)
            embeds_dir = os.path.join(card_dir, "embeds")
            
            if not os.path.isdir(embeds_dir):
                continue
            
            for fname in os.listdir(embeds_dir):
                if not fname.endswith(".npy"):
                    continue
                
                ruta_embedding = os.path.join(embeds_dir, fname)
                resultados.append({
                    "card_id": card_folder,
                    "archivo": fname,
                    "ruta": ruta_embedding,
                    "sufijo": fname.replace(".npy", "")
                })
        
        return resultados
    
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
    
    @staticmethod
    def existe_directorio_carta(card_id: str, catalogo_dir: str = DATA_ROOT) -> bool:
        """Verifica si existe el directorio de una carta."""
        card_dir = os.path.join(catalogo_dir, card_id)
        return os.path.exists(card_dir) and os.path.isdir(card_dir)