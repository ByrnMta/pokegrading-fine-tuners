import io
import os
import uuid
from datetime import datetime
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile, status
try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    Image = None
    HAS_PIL = False
from sqlalchemy.orm import Session

from AccesoDatos.CartasRepositorio import CartasRepositorio
from AccesoDatos.AuditoriaRepositorio import AuditoriaRepositorio
from Esquemas.CartasEsquema import CartaCreate
from Servicios.utilidades.BuscadorImagenes import EmbeddingService

"""Lógica de negocio para el alta de cartas en el catálogo.

Este módulo concentra validaciones, generación de identificadores internos,
persistencia de imágenes y registro de auditoría para mantener el flujo de alta
aislado del controlador.
"""

# Limites y formatos
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "heic"}
MIN_WIDTH = 200
MIN_HEIGHT = 200
UPLOAD_DIR = "uploads"

CANONICAL_RARITIES = {
    "common",
    "uncommon",
    "rare",
    "holo rare",
    "ultra rare",
    "secret rare",
}

VALID_TYPES = {
    "grass",
    "fire",
    "water",
    "lightning",
    "psychic",
    "fighting",
    "darkness",
    "metal",
    "fairy",
    "dragon",
    "colorless",
    "normal",
}

SUPPORTED_LANGUAGES = {
    "es",
    "en",
    "jp",
    "pt",
    "fr",
    "de",
    "it",
}
class CatalogoServicio:
    """Orquesta el alta de cartas y sus efectos colaterales asociados."""

    #============================= Logica endpoints =============================

    @staticmethod
    def agregar_carta(
        db: Session,
        carta_data: CartaCreate,
        imagen_frontal: UploadFile,
        imagen_reverso: UploadFile,
    ) -> dict:
        """Valida, persiste y audita una carta nueva.

        La secuencia es:
        1. Normalizar y validar identidad y datos opcionales.
        2. Verificar que no exista una carta con la misma identidad.
        3. Generar card_id y guardar ambas imágenes.
        4. Crear la carta y su registro de auditoría en la misma transacción.
        """
        errores = {}

        identidad = CatalogoServicio._normalizar_identidad(carta_data, errores)
        display = CatalogoServicio._normalizar_display(carta_data, errores)
        autor = CatalogoServicio._normalizar_texto(carta_data.autor)
        if not autor:
            errores["autor"] = "El autor es obligatorio."

        CatalogoServicio._validar_listas(identidad, display, errores)
        CatalogoServicio._validar_imagen(imagen_frontal, "imagen_frontal", errores)
        CatalogoServicio._validar_imagen(imagen_reverso, "imagen_reverso", errores)

        if errores:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"errores": errores})

        repositorio = CartasRepositorio()
        if repositorio.get_carta_by_identidad(db, identidad=identidad):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La carta con la misma combinación de set, número, edición, idioma y acabado ya existe.",
            )

        card_id = CatalogoServicio._generar_card_id()
        image_front_path, image_back_path = CatalogoServicio._guardar_imagenes(
            card_id=card_id,
            imagen_frontal=imagen_frontal,
            imagen_reverso=imagen_reverso,
            upload_dir=UPLOAD_DIR,
        )

        carta_payload = {**identidad, **display, "autor": autor}
        auditoria_payload = {
            **carta_payload,
            "card_id": card_id,
            "image_front_path": image_front_path,
            "image_back_path": image_back_path,
        }

        auditoria_repo = AuditoriaRepositorio()
        try:
            # Compute and persist embeddings (KISS): read saved image files and persist .npy files
            try:
                emb_svc = EmbeddingService(embeddings_dir="embeddings")
                with open(image_front_path, "rb") as f:
                    front_bytes = f.read()
                back_bytes = None
                if image_back_path:
                    with open(image_back_path, "rb") as f:
                        back_bytes = f.read()
                front_emb = emb_svc.embed_image_bytes(front_bytes)
                back_emb = emb_svc.embed_image_bytes(back_bytes) if back_bytes is not None else None
                emb_svc.persist_embeddings(card_id=card_id, front_emb=front_emb, back_emb=back_emb)
            except Exception as e:
                # If embedding computation/persisting fails, cleanup files and abort
                CatalogoServicio._borrar_archivo(image_front_path)
                CatalogoServicio._borrar_archivo(image_back_path)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al generar embeddings: {e}",
                )

            nueva_carta = repositorio.create_carta(
                db=db,
                carta_data=carta_payload,
                card_id=card_id,
                image_front_path=image_front_path,
                image_back_path=image_back_path,
                estado="ACTIVA",
            )
            auditoria_repo.create_auditoria(
                db=db,
                carta_id=nueva_carta.id,
                card_id=card_id,
                autor=autor,
                datos=auditoria_payload,
            )
            db.commit()
            db.refresh(nueva_carta)
            return nueva_carta
        except HTTPException:
            db.rollback()
            CatalogoServicio._borrar_archivo(image_front_path)
            CatalogoServicio._borrar_archivo(image_back_path)
            raise
        except Exception as e:
            db.rollback()
            CatalogoServicio._borrar_archivo(image_front_path)
            CatalogoServicio._borrar_archivo(image_back_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno al guardar la carta: {e}",
            )

    #============================= Validaciones =============================

    @staticmethod
    def _normalizar_texto(valor: Optional[str]) -> Optional[str]:
        """Elimina espacios vacíos y convierte cadenas vacías en None."""
        if valor is None:
            return None
        valor = str(valor).strip()
        return valor if valor else None

    @staticmethod
    def _normalizar_identidad(carta_data: CartaCreate, errores: dict) -> dict:
        """Extrae y limpia los campos que definen la identidad única de la carta."""
        identidad = {}
        for campo in ["set_name", "numero", "edicion", "idioma", "acabado"]:
            valor = CatalogoServicio._normalizar_texto(getattr(carta_data, campo))
            if not valor:
                errores[campo] = "El campo es obligatorio."
            identidad[campo] = valor
        return identidad

    @staticmethod
    def _normalizar_display(carta_data: CartaCreate, errores: dict) -> dict:
        """Normaliza los campos recomendados y convierte los numéricos."""
        display = {
            "nombre": CatalogoServicio._normalizar_texto(carta_data.nombre),
            "rareza": CatalogoServicio._normalizar_texto(carta_data.rareza),
            "tipo": CatalogoServicio._normalizar_texto(carta_data.tipo),
            "ilustrador": CatalogoServicio._normalizar_texto(carta_data.ilustrador),
        }

        display["hp"] = CatalogoServicio._parse_int(carta_data.hp, "hp", errores, min_value=0)
        display["anio_impresion"] = CatalogoServicio._parse_int(
            carta_data.anio_impresion,
            "anio_impresion",
            errores,
            min_value=1900,
            max_value=datetime.utcnow().year,
        )
        return display

    @staticmethod
    def _parse_int(
        valor: Optional[str],
        campo: str,
        errores: dict,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> Optional[int]:
        """Convierte un texto opcional a entero y valida su rango."""
        if valor is None or str(valor).strip() == "":
            return None
        try:
            valor_int = int(str(valor).strip())
        except ValueError:
            errores[campo] = "Debe ser numerico."
            return None
        if min_value is not None and valor_int < min_value:
            errores[campo] = f"Debe ser mayor o igual a {min_value}."
            return None
        if max_value is not None and valor_int > max_value:
            errores[campo] = f"Debe ser menor o igual a {max_value}."
            return None
        return valor_int

    @staticmethod
    def _validar_listas(identidad: dict, display: dict, errores: dict) -> None:
        """Valida que los valores pertenezcan a los catálogos permitidos."""
        idioma = identidad.get("idioma")
        if idioma and idioma.lower() not in SUPPORTED_LANGUAGES:
            errores["idioma"] = "Idioma no soportado."

        rareza = display.get("rareza")
        if rareza and rareza.lower() not in CANONICAL_RARITIES:
            errores["rareza"] = "Rareza fuera del listado canonico."

        tipo = display.get("tipo")
        if tipo and tipo.lower() not in VALID_TYPES:
            errores["tipo"] = "Tipo fuera del listado valido."

    @staticmethod
    def _validar_imagen(imagen: UploadFile, campo: str, errores: dict) -> None:
        """Valida presencia, extensión, tamaño y resolución mínima de una imagen."""
        if not imagen or not getattr(imagen, "filename", None):
            errores[campo] = "No se ha subido ninguna imagen."
            return

        extension = CatalogoServicio._obtener_extension(imagen.filename)
        if not extension or extension not in ALLOWED_EXTENSIONS:
            errores[campo] = "Extension de archivo no permitida."
            return

        size = CatalogoServicio._obtener_tamano(imagen)
        if size > MAX_FILE_SIZE:
            errores[campo] = f"El tamano no puede exceder {MAX_FILE_SIZE // (1024 * 1024)} MB."
            return

        if not HAS_PIL:
            errores[campo] = "Dependencia Pillow no encontrada en el servidor."
            return

        if not CatalogoServicio._validar_resolucion(imagen):
            errores[campo] = f"Resolucion insuficiente: minimo {MIN_WIDTH}x{MIN_HEIGHT}px."

    @staticmethod
    def _obtener_extension(nombre_archivo: str) -> Optional[str]:
        """Retorna la extensión normalizada del archivo o None si no existe."""
        if "." not in nombre_archivo:
            return None
        return nombre_archivo.rsplit(".", 1)[-1].lower()

    @staticmethod
    def _obtener_tamano(imagen: UploadFile) -> int:
        """Obtiene el tamaño del archivo sin alterar el cursor final."""
        imagen.file.seek(0, os.SEEK_END)
        size = imagen.file.tell()
        imagen.file.seek(0)
        return size

    @staticmethod
    def _validar_resolucion(imagen: UploadFile) -> bool:
        """Comprueba que la imagen cumpla la resolución mínima requerida."""
        try:
            contenido = imagen.file.read()
            imagen.file.seek(0)
            with Image.open(io.BytesIO(contenido)) as img:
                width, height = img.size
                return width >= MIN_WIDTH and height >= MIN_HEIGHT
        except Exception:
            return False

    #============================= Utilidades =============================

    @staticmethod
    def _generar_card_id() -> str:
        """Genera un identificador interno único e inmutable para la carta."""
        return str(uuid.uuid4())

    @staticmethod
    def _guardar_imagenes(
        card_id: str,
        imagen_frontal: UploadFile,
        imagen_reverso: UploadFile,
        upload_dir: str,
    ) -> Tuple[str, str]:
        """Guarda ambas imágenes y revierte la primera si la segunda falla."""
        ruta_frontal = CatalogoServicio._guardar_imagen(card_id, "front", imagen_frontal, upload_dir)
        try:
            ruta_reverso = CatalogoServicio._guardar_imagen(card_id, "back", imagen_reverso, upload_dir)
        except Exception:
            CatalogoServicio._borrar_archivo(ruta_frontal)
            raise
        return ruta_frontal, ruta_reverso

    @staticmethod
    def _guardar_imagen(card_id: str, sufijo: str, imagen: UploadFile, upload_dir: str) -> str:
        """Persiste una imagen en disco usando el card_id como prefijo."""
        try:
            extension = CatalogoServicio._obtener_extension(imagen.filename)
            nombre_archivo = f"{card_id}_{sufijo}.{extension}"
            os.makedirs(upload_dir, exist_ok=True)
            ruta_archivo = os.path.join(upload_dir, nombre_archivo)

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
    def _borrar_archivo(ruta_archivo: Optional[str]) -> None:
        """Elimina un archivo si existe, ignorando errores de limpieza."""
        if not ruta_archivo:
            return
        try:
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
        except Exception:
            return
        