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

    # Constantes usadas en la evaluación de la imagen
    TAMANO_REDIMENSIONADO = (800, 800)
    DIVISOR_BORDE = 20.0
    MAX_PUNTUACION = 1.0
    REFERENCIA_BRILLO = 128.0
    CONTRASTE_DIVISOR = 64.0
    RADIO_BANDA_CENTRAL = 0.1
    NORMALIZACION_ENCUADRE = 1.2
    DIVISOR_MEDIA_EXTERIOR = 10.0
    EPS = 1e-6

    def validar_tamaño_imagen(db: Session, imagen: UploadFile, id_usuario: int, errores: dict):
        """Valida que el tamaño de la imagen no exceda los 10MB."""

        # Se valida que el tamaño máximo de la imagen sea 10 MB
        if imagen.size > EvaluacionCartaValidacion.TAMANO_MAXIMO_IMAGEN:
            errores["imagen tamaño"] = "El tamaño de la imagen no debe exceder los 10MB."
            errores["status_code"] = 422
            agregar_log_evaluacion_carta_fallida("El tamaño de la imagen excede el límite permitido.", id_usuario)
            return None

    def validar_formato_imagen(db: Session, imagen: UploadFile, id_usuario: int, errores: dict):
        """Valida que el formato de la imagen sea JPEG, PNG o HEIC."""

        # Se valida que el formato de la imagen sea JPEG, PNG o HEIC
        extension = imagen.filename.split(".")[-1].lower() if "." in imagen.filename else ""
        if extension not in EvaluacionCartaValidacion.EXTENSIONES_PERMITIDAS:
            errores["imagen formato"] = "El formato de la imagen debe ser JPEG, PNG o HEIC."
            errores["status_code"] = 422
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
            errores["status_code"] = 422
            agregar_log_evaluacion_carta_fallida("No se pudo leer la imagen para validación de contenido.", id_usuario)
            return None
                
        # Se valida que el archivo no esté vacío
        if not data:
            errores["imagen contenido"] = "La imagen está vacía."
            errores["status_code"] = 422
            agregar_log_evaluacion_carta_fallida("La imagen está vacía.", id_usuario)
            return None

        # Se valida que el archivo sea una imagen válida
        try:
            Image.open(BytesIO(data)).verify()
        except (UnidentifiedImageError, OSError, ValueError):
            errores["imagen contenido"] = "El archivo no es una imagen valida (corrupto)."
            errores["status_code"] = 422
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
                    errores["status_code"] = 422
                    agregar_log_evaluacion_carta_fallida("La imagen contiene datos extra luego del fin de la imagen.", id_usuario)
                    return None
                
        except (UnidentifiedImageError, OSError, ValueError):
            errores["imagen contenido"] = "El archivo no es una imagen valida."
            errores["status_code"] = 422
            agregar_log_evaluacion_carta_fallida("El archivo no es una imagen válida.", id_usuario)
            return None
        
    def validar_calidad_imagen(db: Session, imagen: UploadFile, id_usuario: int, errores: dict):
        """Valida que la imagen tenga una calidad suficiente que supere un umbral mínimo.
        En cuanto a borrosidad, encuandre y iluminación."""
        
        # Se carga y se prepara la imagen (en la validación anterior se validó que no sea corrupto)
        imagen.file.seek(0)
        data = imagen.file.read()
        img = Image.open(BytesIO(data))
        img.load()
        
        # Se pasa la imagen a escala de grises y se redimensiona a un misma proporción
        gray = EvaluacionCartaValidacion.pasar_a_escala_grises_y_redimensionar(img)

        # Se mide la borrosidad
        blur_score, edges = EvaluacionCartaValidacion.medir_borrosidad(gray)

        # Se mide la iluminación
        lighting_score = EvaluacionCartaValidacion.medir_iluminacion(gray)

        # Se mide el encuadre (la idea es que los bordes de la carta estén en los bordes de la imagen)
        framing_score = EvaluacionCartaValidacion.medir_encuadre(gray, edges)

        # se combinan las métricas con sus pesos para obtener un índice de calidad de imagen (IQS)
        pesos = EvaluacionCartaValidacion.IQS_PESOS
        iqs = (
            blur_score * pesos["borrosidad"]
            + framing_score * pesos["encuadre"]
            + lighting_score * pesos["iluminacion"]
        )

        causas = [] # se almacenan las causas de rechazo de la imagen

        if blur_score < EvaluacionCartaValidacion.IQS_MIN_METRICA:
            causas.append("borroso")
        if framing_score < EvaluacionCartaValidacion.IQS_MIN_METRICA:
            causas.append("mal encuadre")
        if lighting_score < EvaluacionCartaValidacion.IQS_MIN_METRICA:
            causas.append("mala iluminacion")

        if iqs < EvaluacionCartaValidacion.IQS_UMBRAL_MINIMO:
            detalle = ", ".join(causas) if causas else "calidad insuficiente"
            errores["imagen calidad"] = f"Rechazo por {detalle}."
            errores["status_code"] = 422
            agregar_log_evaluacion_carta_fallida(f"Rechazo por calidad insuficiente: {detalle}.", id_usuario)
            return None

    def pasar_a_escala_grises_y_redimensionar(img: Image.Image) -> Image.Image:
        """Se pasa la imagen a escala de grises y se redimensiona a un misma proporción para que el procesamiento sea más rapido"""
        
        gray = img.convert("L")
        gray.thumbnail(EvaluacionCartaValidacion.TAMANO_REDIMENSIONADO)
        return gray

    def medir_borrosidad(gray: Image.Image) -> float:
        """Se mide la borrosidad de la imagen utilizando un filtro de bordes y calculando el promedio del brillo de los bordes."""

        edges = gray.filter(ImageFilter.FIND_EDGES) # aplica un filtro que resalta los bordes, cambios bruscos quedan blanco y zonas uniformes en negro
        edge_mean = ImageStat.Stat(edges).mean[0] # hace un promedio del brillo de esa imagen de bordes

        # Normaliza el valor a un rango de 0 a 1, valor cercano a 1 indica imagen nítida
        blur_score = min(
            EvaluacionCartaValidacion.MAX_PUNTUACION,
            edge_mean / EvaluacionCartaValidacion.DIVISOR_BORDE,
        )
        return blur_score, edges
    
    def medir_iluminacion(gray: Image.Image) -> float:
        """Se mide la iluminación de la imagen, considerando tanto el brillo como el contraste."""

        stat = ImageStat.Stat(gray)
        brightness = stat.mean[0] # se toma el brillo promedio de la imagen
        contrast = stat.stddev[0] # se toma la disperción de los valores
        brightness_score = max(
            0.0,
            1.0 - abs(brightness - EvaluacionCartaValidacion.REFERENCIA_BRILLO) / EvaluacionCartaValidacion.REFERENCIA_BRILLO,
        )
        contrast_score = min(
            EvaluacionCartaValidacion.MAX_PUNTUACION,
            contrast / EvaluacionCartaValidacion.CONTRASTE_DIVISOR,
        )
        lighting_score = (brightness_score + contrast_score) / 2.0

        return lighting_score
    
    def medir_encuadre(gray: Image.Image, edges: Image.Image) -> float:
        """Se mide el encuadre de la imagen, considerando la relación entre el brillo de los bordes exteriores y el brillo del centro de la imagen."""
        
        w, h = gray.size
        band_x = max(1, int(w * EvaluacionCartaValidacion.RADIO_BANDA_CENTRAL))
        band_y = max(1, int(h * EvaluacionCartaValidacion.RADIO_BANDA_CENTRAL))
        outer = edges.crop((0, 0, w, h))
        center = edges.crop((band_x, band_y, w - band_x, h - band_y))

        outer_mean = ImageStat.Stat(outer).mean[0]
        center_mean = (
            ImageStat.Stat(center).mean[0]
            if center.size[0] > 0 and center.size[1] > 0
            else 0.0
        )
        ratio = outer_mean / (center_mean + EvaluacionCartaValidacion.EPS)
        framing_score = (
            min(EvaluacionCartaValidacion.MAX_PUNTUACION, ratio / EvaluacionCartaValidacion.NORMALIZACION_ENCUADRE)
            * min(EvaluacionCartaValidacion.MAX_PUNTUACION, outer_mean / EvaluacionCartaValidacion.DIVISOR_MEDIA_EXTERIOR)
        )

        return framing_score
