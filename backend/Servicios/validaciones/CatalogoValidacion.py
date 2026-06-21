import io
import os
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, UploadFile, status
from Esquemas.CartasEsquema import CartaCreate

try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    Image = None
    HAS_PIL = False

"""Validaciones para el catálogo de cartas.

Este módulo concentra todas las validaciones necesarias para el alta de cartas,
incluyendo validaciones de datos, imágenes y formatos.
"""

# Límites y formatos
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "heic"}
MIN_WIDTH = 200
MIN_HEIGHT = 200

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

class CatalogoValidacion:
    """Clase con métodos estáticos para validaciones del catálogo."""
    
    @staticmethod
    def normalizar_texto(valor: Optional[str]) -> Optional[str]:
        """Elimina espacios vacíos y convierte cadenas vacías en None."""
        if valor is None:
            return None
        valor = str(valor).strip()
        return valor if valor else None

    @staticmethod
    def validar_identidad(carta_data: CartaCreate, errores: dict) -> dict:
        """Extrae y limpia los campos que definen la identidad única de la carta."""
        identidad = {}
        for campo in ["set_name", "numero", "edicion", "idioma", "acabado"]:
            valor = CatalogoValidacion.normalizar_texto(getattr(carta_data, campo))
            if not valor:
                errores[campo] = "El campo es obligatorio."
            identidad[campo] = valor
        return identidad

    @staticmethod
    def validar_display(carta_data: CartaCreate, errores: dict) -> dict:
        """Normaliza los campos recomendados y convierte los numéricos."""
        display = {
            "nombre": CatalogoValidacion.normalizar_texto(carta_data.nombre),
            "rareza": CatalogoValidacion.normalizar_texto(carta_data.rareza),
            "tipo": CatalogoValidacion.normalizar_texto(carta_data.tipo),
            "ilustrador": CatalogoValidacion.normalizar_texto(carta_data.ilustrador),
        }

        display["hp"] = CatalogoValidacion.parse_int(carta_data.hp, "hp", errores, min_value=0)
        display["anio_impresion"] = CatalogoValidacion.parse_int(
            carta_data.anio_impresion,
            "anio_impresion",
            errores,
            min_value=1900,
            max_value=datetime.utcnow().year,
        )
        return display

    @staticmethod
    def parse_int(
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
    def validar_listas(identidad: dict, display: dict, errores: dict) -> None:
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
    def validar_imagen(imagen: UploadFile, campo: str, errores: dict) -> None:
        """Valida presencia, extensión, tamaño y resolución mínima de una imagen."""
        if not imagen or not getattr(imagen, "filename", None):
            errores[campo] = "No se ha subido ninguna imagen."
            return

        extension = CatalogoValidacion.obtener_extension(imagen.filename)
        if not extension or extension not in ALLOWED_EXTENSIONS:
            errores[campo] = "Extension de archivo no permitida."
            return

        size = CatalogoValidacion.obtener_tamano(imagen)
        if size > MAX_FILE_SIZE:
            errores[campo] = f"El tamano no puede exceder {MAX_FILE_SIZE // (1024 * 1024)} MB."
            return

        if not HAS_PIL:
            errores[campo] = "Dependencia Pillow no encontrada en el servidor."
            return

        if not CatalogoValidacion.validar_resolucion(imagen):
            errores[campo] = f"Resolucion insuficiente: minimo {MIN_WIDTH}x{MIN_HEIGHT}px."

    @staticmethod
    def obtener_extension(nombre_archivo: str) -> Optional[str]:
        """Retorna la extensión normalizada del archivo o None si no existe."""
        if "." not in nombre_archivo:
            return None
        return nombre_archivo.rsplit(".", 1)[-1].lower()

    @staticmethod
    def obtener_tamano(imagen: UploadFile) -> int:
        """Obtiene el tamaño del archivo sin alterar el cursor final."""
        imagen.file.seek(0, os.SEEK_END)
        size = imagen.file.tell()
        imagen.file.seek(0)
        return size

    @staticmethod
    def validar_resolucion(imagen: UploadFile) -> bool:
        """Comprueba que la imagen cumpla la resolución mínima requerida."""
        try:
            contenido = imagen.file.read()
            imagen.file.seek(0)
            with Image.open(io.BytesIO(contenido)) as img:
                width, height = img.size
                return width >= MIN_WIDTH and height >= MIN_HEIGHT
        except Exception:
            return False

    @staticmethod
    def validar_autor(autor: Optional[str], errores: dict) -> Optional[str]:
        """Valida y normaliza el autor."""
        autor_normalizado = CatalogoValidacion.normalizar_texto(autor)
        if not autor_normalizado:
            errores["autor"] = "El autor es obligatorio."
            return None
        return autor_normalizado