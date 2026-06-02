from io import BytesIO
from fastapi import UploadFile
from PIL import Image, ImageFilter, ImageStat, UnidentifiedImageError
from sqlalchemy.orm import Session
from Servicios.utilidades.AuditoriaUtilidad import agregar_log_evaluacion_carta_fallida

class EvaluacionCartaValidacion:

    TAMANO_MAXIMO_IMAGEN = 10 * 1024 * 1024  # 10MB
    EXTENSIONES_PERMITIDAS = {"jpeg", "png", "heic"}

    # umbral mínimo final de calidad de imagen (con los tres parametros combinados)
    IQS_UMBRAL_MINIMO = 0.7 

    # Parámetros y sus pesos
    IQS_PESOS = {"borrosidad": 0.4, "encuadre": 0.3, "iluminacion": 0.3}

    # Umbral mínimo por cada parámetro (borrosidad, encuadre e iluminación) y así poder identificar la causa especifica
    IQS_MIN_METRICA = 0.7

    def validar_tamaño_imagen(db: Session, imagen: UploadFile, id_usuario: int, errores: dict):
        """Valida que el tamaño de la imagen no exceda los 10MB."""

        # Se valida que el tamaño máximo de la imagen sea 10 MB
        if imagen.size > EvaluacionCartaValidacion.TAMANO_MAXIMO_IMAGEN:
            errores['imagen tamaño'] = "El tamaño de la imagen no debe exceder los 10MB."
            agregar_log_evaluacion_carta_fallida("El tamaño de la imagen excede el límite permitido.", id_usuario)
            return None

    def validar_formato_imagen(db: Session, imagen: UploadFile, id_usuario: int, errores: dict):
        """Valida que el formato de la imagen sea JPEG, PNG o HEIC."""

        # Se valida que el formato de la imagen sea JPEG, PNG o HEIC
        extension = imagen.filename.split(".")[-1].lower() if "." in imagen.filename else ""
        if extension not in EvaluacionCartaValidacion.EXTENSIONES_PERMITIDAS:
            errores['imagen formato'] = "El formato de la imagen debe ser JPEG, PNG o HEIC."
            agregar_log_evaluacion_carta_fallida("El formato de la imagen no es válido.", id_usuario)
            return None

    def validar_deteccion_polyglot(db: Session, imagen: UploadFile, id_usuario: int, errores: dict):
        """Valida que la imagen no contenga texto en múltiples idiomas (polyglot)."""

        # Se valida que la imagen no contenga texto en múltiples idiomas (polyglot)
        try:
            imagen.file.seek(0)
            data = imagen.file.read()
        except Exception:
            errores["imagen contenido"] = "No se pudo leer la imagen."
            agregar_log_evaluacion_carta_fallida("No se pudo leer la imagen para validación de contenido.", id_usuario)
            return None
                
        # Se valida que el archivo no esté vacío
        if not data:
            errores["imagen contenido"] = "La imagen está vacía."
            agregar_log_evaluacion_carta_fallida("La imagen está vacía.", id_usuario)
            return None

        # Se valida que el archivo sea una imagen válida
        try:
            Image.open(BytesIO(data)).verify()
        except (UnidentifiedImageError, OSError, ValueError):
            errores["imagen contenido"] = "El archivo no es una imagen valida (corrupto)."
            agregar_log_evaluacion_carta_fallida("El archivo no es una imagen válida (corrupto).", id_usuario)
            return None

        # Se valida que la imagen no contenga datos extra luego del fin de la imagen
        try:
            img = Image.open(BytesIO(data))
            img.load()

            if img.fp is not None:
                trailing = img.fp.read()
                if trailing not in (b"", None):
                    errores["imagen contenido"] = "La imagen contiene datos extra."
                    agregar_log_evaluacion_carta_fallida("La imagen contiene datos extra luego del fin de la imagen.", id_usuario)
                    return None
        except (UnidentifiedImageError, OSError, ValueError):
            errores["imagen contenido"] = "El archivo no es una imagen valida."
            agregar_log_evaluacion_carta_fallida("El archivo no es una imagen válida.", id_usuario)
            return None
        
    def validar_calidad_imagen(db: Session, imagen: UploadFile, id_usuario: int, errores: dict):
        """Valida que la imagen tenga una calidad suficiente que supere un umbral mínimo.
        En cuanto a borrosidad, encuandre y iluminación."""

        # Primero parte
        imagen.file.seek(0)
        data = imagen.file.read()
        img = Image.open(BytesIO(data))
        img.load()
        
        # Segunda parte
        gray = img.convert("L")
        gray.thumbnail((800, 800))

        # Tercera parte:
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_mean = ImageStat.Stat(edges).mean[0]
        
        # Cuarta parte:
        blur_score = min(1.0, edge_mean / 20.0)

        # Quinta parte:
        stat = ImageStat.Stat(gray)
        brightness = stat.mean[0]
        contrast = stat.stddev[0]
        brightness_score = max(0.0, 1.0 - abs(brightness - 128.0) / 128.0)
        contrast_score = min(1.0, contrast / 64.0)
        lighting_score = (brightness_score + contrast_score) / 2.0

        # Sexta parte:
        w, h = gray.size
        band_x = max(1, int(w * 0.1))
        band_y = max(1, int(h * 0.1))
        outer = edges.crop((0, 0, w, h))
        center = edges.crop((band_x, band_y, w - band_x, h - band_y))

        # Séptima parte:
        outer_mean = ImageStat.Stat(outer).mean[0]
        center_mean = ImageStat.Stat(center).mean[0] if center.size[0] > 0 and center.size[1] > 0 else 0.0
        ratio = outer_mean / (center_mean + 1e-6)
        framing_score = min(1.0, ratio / 1.2) * min(1.0, outer_mean / 10.0)

        # Octava parte: se combinan las métricas con sus pesos para obtener un índice de calidad de imagen (IQS)
        pesos = EvaluacionCartaValidacion.IQS_PESOS
        iqs = (
            blur_score * pesos["borrosidad"]
            + framing_score * pesos["encuadre"]
            + lighting_score * pesos["iluminacion"]
        )

        causas = []
        if blur_score < EvaluacionCartaValidacion.IQS_MIN_METRICA:
            causas.append("borroso")
        if framing_score < EvaluacionCartaValidacion.IQS_MIN_METRICA:
            causas.append("mal encuadre")
        if lighting_score < EvaluacionCartaValidacion.IQS_MIN_METRICA:
            causas.append("mala iluminacion")

        if iqs < EvaluacionCartaValidacion.IQS_UMBRAL_MINIMO:
            detalle = ", ".join(causas) if causas else "calidad insuficiente"
            errores["imagen calidad"] = f"Rechazo por {detalle}."
            agregar_log_evaluacion_carta_fallida(f"Rechazo por calidad insuficiente: {detalle}.", id_usuario)
            return None

