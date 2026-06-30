from __future__ import annotations

import io
import math
from dataclasses import dataclass
from typing import Optional, Tuple
from PreprocesarCartaUtilidad_refact import _ordenar_puntos
from fastapi import UploadFile

import cv2
import numpy as np
from skimage import exposure, filters

# ---------------------------------------------------------------------------
# Constantes de configuración
# ---------------------------------------------------------------------------

# Relación de aspecto estándar de una carta (Pokémon, MTG, TCG)
RELACION_ASPECTO_TARJETA = 63.5 / 88.0   # ancho / alto = 0.721
TOLERANCIA_RELACION_ASPECTO = 0.12      # +-12 % de tolerancia

# Salida canónica en píxeles
ANCHO_CANONICO = 630 # ancho de la carta en píxeles para la imagen corregida
ALTO_CANONICO = 880 # alto de la carta en píxeles para la imagen corregida

# Grosor de cada región 
BANDA_CENTRADO = 0.08    # banda de borde que se usa para medir el centrado de la carta en la imagen original
TAMANO_ESQUINA = 0.12    # tamaño del cuadrado de esquina (fracción del lado corto)
GROSOR_BORDE = 0.06      # grosor de la franja de borde (fracción del lado corto)

# Umbrales de descarte
FRACCION_MINIMA_AREA_TARJETA = 0.05   # la carta debe ocupar al menos el 5 % de la imagen
ANGULO_MAXIMO_CORREGIBLE = 45.0   # ángulo máximo corregible; más distorsión irrecuperable

# Corners
TOLERANCIA_LAP_ESQUINA = 4000.0   # entre más alto más permisivo con desgaste
PESO_LAP_ESQUINA = 10.0           # entre más alto más penaliza el desgaste
TOLERANCIA_RATIO_ESQUINA = 0.5     # entre más alto más permisivo con el filo

# Edges
TOLERANCIA_BRILLO_BORDE = 800.0   # entre más alto más permisivo con variación de brillo
PESO_BRILLO_BORDE = 60.0   # peso del brillo en el score final
TOLERANCIA_RUIDO_BORDE = 1200.0  # entre más alto más permisivo con ruido (el ruido se mide con la varianza de Laplaciano)
PESO_RUIDO_BORDE = 40.0   # peso del ruido en el score final

# Surface
TOLERANCIA_LAP_SUPERFICIE = 8000.0  # entre más alto más permisivo con rayones
PESO_LAP_SUPERFICIE = 35.0   # peso de rayones en el score final
TOLERANCIA_MANCHAS_SUPERFICIE = 100.0   # entre más alto más permisivo con manchas
PESO_MANCHAS_SUPERFICIE = 35.0   # peso de manchas en el score final
TOLERANCIA_COLOR_SUPERFICIE = 600.0   # entre más alto más permisivo con decoloración
PESO_COLOR_SUPERFICIE = 30.0   # peso de decoloración en el score final

# Escala general de los puntajes (scores) de 0 a 100
PUNTAJE_MINIMO = 0
PUNTAJE_MAXIMO = 100

# ---------------------------------------------------------------------------
# Tipos internos
# ---------------------------------------------------------------------------

@dataclass
class ContornoTarjeta:
    """Información del contorno detectado de la carta."""
    cuadrilatero: np.ndarray   # 4 puntos (x, y) ordenados
    area: float
    angulo_grados: float       # ángulo de inclinación estimado

@dataclass
class ResultadoEvaluacion:
    centrado:   Optional[float]
    esquinas:   Optional[float]
    bordes:     Optional[float]
    superficie: Optional[float]


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def analizar_carta(image: UploadFile, errores: dict) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Recibe un UploadFile (imagen ya validada y limpia) y regresa (centering, corners, edges, surface) floats 0-100,
    o (None, None, None, None) si el procesamiento falla.
    """

    # Leer bytes y decodificar la imagen
    image.file.seek(0)
    imagen_bytes = image.file.read()
    img_bgr = decodificar_imagen(imagen_bytes) # es un np.ndarray de OpenCV en formato BGR
    if img_bgr is None:
        errores["imagen"] = "No se pudo decodificar la imagen. Asegúrese de que sea un archivo de imagen válido."
        return None, None, None, None

    # Detectar y aislar la carta
    contorno_tarjeta = detectar_contorno_tarjeta(img_bgr)
    if contorno_tarjeta is None:
        print("analizar_carta: no se pudo aislar la carta del fondo: revisión manual.")
        return None, None, None, None

    # Validar que la distorsión sea corregible
    if contorno_tarjeta.angulo_grados > ANGULO_MAXIMO_CORREGIBLE:
        errores["imagen"] = "Distorsión irrecuperable. Por favor, recapture la imagen."
        return None, None, None, None

    # Corrección de perspectiva: imagen canónica de la carta
    imagen_corregida_perspectiva = corregir_perspectiva(img_bgr, contorno_tarjeta.cuadrilatero)

    # Normalizar color e iluminación
    imagen_normalizada = normalizar_color(imagen_corregida_perspectiva)

    # Calcular scores
    score_centrado = calcular_score_centrado(imagen_normalizada, contorno_tarjeta.cuadrilatero, img_bgr.shape)
    score_esquinas = calcular_score_esquinas(imagen_normalizada)
    score_bordes = calcular_score_bordes(imagen_normalizada)
    score_superficie = calcular_score_superficie(imagen_normalizada)

    return score_centrado, score_esquinas, score_bordes, score_superficie

# ---------------------------------------------------------------------------
# Decodificación de imagen
# ---------------------------------------------------------------------------

def decodificar_imagen(datos_imagen: bytes) -> Optional[np.ndarray]:
    """Convierte bytes en imagen BGR de OpenCV."""

    array_numpy = np.frombuffer(datos_imagen, dtype=np.uint8) # se convierten los bytes a array numpy
    imagen_decodificada = cv2.imdecode(array_numpy, cv2.IMREAD_COLOR)
    return imagen_decodificada  # None si falla

# ---------------------------------------------------------------------------
# Detección de la carta
# ---------------------------------------------------------------------------

def detectar_contorno_tarjeta(imagen: np.ndarray) -> Optional[ContornoTarjeta]:
    """
    Intenta localizar el cuadrilátero de la carta en la imagen.
    Retorna None si no se encuentra un candidato válido.
    """
    # Parámetros del pre-procesamiento de bordes
    TAMANO_KERNEL_DESENFOQUE = (5, 5) # tamaño de la ventana para el desenfoque gaussiano
    UMBRAL_CANNY_INFERIOR = 30
    UMBRAL_CANNY_SUPERIOR = 120
    ITERACIONES_DILATACION = 2
    NUMERO_CANDIDATOS_A_EVALUAR = 8
    FACTOR_APROXIMACION_POLIGONO = 0.02
    NUMERO_VERTICES_CUADRILATERO = 4

    alto_imagen, ancho_imagen = imagen.shape[:2]
    area_imagen = alto_imagen * ancho_imagen

    # Preprocesamiento para detección de bordes
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    imagen_difuminada = cv2.GaussianBlur(imagen_gris, TAMANO_KERNEL_DESENFOQUE, 0)
    imagen_bordes = cv2.Canny(imagen_difuminada, UMBRAL_CANNY_INFERIOR, UMBRAL_CANNY_SUPERIOR)
    imagen_bordes = cv2.dilate(imagen_bordes, None, iterations=ITERACIONES_DILATACION)

    # Buscar contornos y filtrar por área y forma
    contornos, _ = cv2.findContours(imagen_bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None

    # Ordenar por área descendente y probar los mejores candidatos
    contornos = sorted(contornos, key=cv2.contourArea, reverse=True)

    for contorno in contornos[:NUMERO_CANDIDATOS_A_EVALUAR]:
        area_contorno = cv2.contourArea(contorno)
        if area_contorno < area_imagen * FRACCION_MINIMA_AREA_TARJETA:
            break  # los siguientes serán menores
        
        # Aproximar el contorno a un polígono y verificar si es un cuadrilátero
        perimetro = cv2.arcLength(contorno, True)
        aproximacion = cv2.approxPolyDP(contorno, FACTOR_APROXIMACION_POLIGONO * perimetro, True)

        if len(aproximacion) != NUMERO_VERTICES_CUADRILATERO:
            continue
        
        # Ordenar los puntos del cuadrilátero: top-left, top-right, bottom-right, bottom-left
        cuadrilatero = ordenar_puntos(aproximacion.reshape(4, 2).astype(np.float32))

        # Validar relación de aspecto
        ancho_tarjeta, alto_tarjeta = dimensiones_cuadrilatero(cuadrilatero)
        if alto_tarjeta == 0:
            continue

        relacion_aspecto = ancho_tarjeta / alto_tarjeta
        if abs(relacion_aspecto - RELACION_ASPECTO_TARJETA) > TOLERANCIA_RELACION_ASPECTO:
            # Intentar orientación vertical invertida
            if abs((alto_tarjeta / ancho_tarjeta) - RELACION_ASPECTO_TARJETA) <= TOLERANCIA_RELACION_ASPECTO:
                cuadrilatero = ordenar_puntos(cuadrilatero[[1, 2, 3, 0]])  # rotar puntos
                ancho_tarjeta, alto_tarjeta = alto_tarjeta, ancho_tarjeta
            else:
                continue
        
        # Estimar ángulo de inclinación
        angulo = estimar_inclinacion(cuadrilatero)
        return ContornoTarjeta(cuadrilatero=cuadrilatero, area=area_contorno, angulo_grados=angulo)

    return None  # cuando ningún candidato es válido


def ordenar_puntos(puntos: np.ndarray) -> np.ndarray:
    """Ordena 4 puntos: top-left, top-right, bottom-right, bottom-left."""

    INDICE_SUPERIOR_IZQUIERDO = 0
    INDICE_SUPERIOR_DERECHO = 1
    INDICE_INFERIOR_DERECHO = 2
    INDICE_INFERIOR_IZQUIERDO = 3

    puntos_ordenados = np.zeros((4, 2), dtype=np.float32)
    suma_coordenadas = puntos.sum(axis=1)
    puntos_ordenados[INDICE_SUPERIOR_IZQUIERDO] = puntos[np.argmin(suma_coordenadas)]   # top-left
    puntos_ordenados[INDICE_INFERIOR_DERECHO] = puntos[np.argmax(suma_coordenadas)]   # bottom-right
    diferencia_coordenadas = np.diff(puntos, axis=1)
    puntos_ordenados[INDICE_SUPERIOR_DERECHO] = puntos[np.argmin(diferencia_coordenadas)]  # top-right
    puntos_ordenados[INDICE_INFERIOR_IZQUIERDO] = puntos[np.argmax(diferencia_coordenadas)]  # bottom-left

    return puntos_ordenados

def dimensiones_cuadrilatero(cuadrilatero: np.ndarray) -> Tuple[float, float]:
    """Ancho y alto aproximados del cuadrilátero."""

    superior_izq, superior_der, inferior_der, inferior_izq = cuadrilatero # puntos en orden: top-left, top-right, bottom-right, bottom-left
    ancho = (np.linalg.norm(superior_der - superior_izq) + np.linalg.norm(inferior_der - inferior_izq)) / 2 # promedio de los dos lados horizontales
    alto  = (np.linalg.norm(inferior_izq - superior_izq) + np.linalg.norm(inferior_der - superior_der)) / 2 # promedio de los dos lados verticales

    return float(ancho), float(alto)


def estimar_inclinacion(cuadrilatero: np.ndarray) -> float:
    """Ángulo de inclinación en grados (respecto al eje horizontal)."""

    punto_superior_izq, punto_superior_der = cuadrilatero[0], cuadrilatero[1]
    diferencia_x = punto_superior_der[0] - punto_superior_izq[0] # esta diferencia quiere decir que la carta está inclinada hacia la derecha
    diferencia_y = punto_superior_der[1] - punto_superior_izq[1] # esta diferencia quiere decir que la carta está inclinada hacia abajo

    return abs(math.degrees(math.atan2(diferencia_y, diferencia_x)))

# ---------------------------------------------------------------------------
# Corrección de perspectiva
# ---------------------------------------------------------------------------

def corregir_perspectiva(imagen: np.ndarray, cuadrilatero: np.ndarray) -> np.ndarray:
    """
    Aplica transformación de perspectiva para obtener una vista frontal
    de la carta con tamaño canónico ANCHO_CANONICO * ALTO_CANONICO.
    """

    # Puntos de destino para la transformación de perspectiva
    puntos_destino = np.array([
        [0,                  0],
        [ANCHO_CANONICO - 1, 0],
        [ANCHO_CANONICO - 1, ALTO_CANONICO - 1],
        [0,                  ALTO_CANONICO - 1],
    ], dtype=np.float32)

    # Se obtiene la matriz de transformación y se aplica a la imagen
    matriz_transformacion = cv2.getPerspectiveTransform(cuadrilatero, puntos_destino)
    imagen_corregida = cv2.warpPerspective(imagen, matriz_transformacion, (ANCHO_CANONICO, ALTO_CANONICO))

    return imagen_corregida

# ---------------------------------------------------------------------------
# Normalización de color e iluminación
# ---------------------------------------------------------------------------

def normalizar_color(imagen: np.ndarray) -> np.ndarray:
    """
    Normaliza la iluminación con CLAHE en el canal L (Lab)
    y ajusta el balance de blancos con corrección de escala de grises.
    """

    VALOR_NEUTRO_LAB = 128
    VALOR_MINIMO_CANAL = 0
    VALOR_MAXIMO_CANAL = 255
    LIMITE_RECORTE_CLAHE = 2.0 # CLAHE quiere decir "Contrast Limited Adaptive Histogram Equalization"
    TAMANO_CUADRICULA_CLAHE = (8, 8)

    # Balance de blancos (escala de grises)
    imagen_lab = cv2.cvtColor(imagen, cv2.COLOR_BGR2LAB).astype(np.float32)
    promedio_canal_a = np.mean(imagen_lab[:, :, 1]) # canal a (verde-rojo)
    promedio_canal_b = np.mean(imagen_lab[:, :, 2]) # canal b (azul-amarillo)
    imagen_lab[:, :, 1] -= (promedio_canal_a - VALOR_NEUTRO_LAB) # se ajusta el canal a para que su promedio sea VALOR_NEUTRO_LAB
    imagen_lab[:, :, 2] -= (promedio_canal_b - VALOR_NEUTRO_LAB) # se ajusta el canal b para que su promedio sea VALOR_NEUTRO_LAB

    imagen_lab = np.clip(imagen_lab, VALOR_MINIMO_CANAL, VALOR_MAXIMO_CANAL).astype(np.uint8) # se asegura que los valores estén en el rango 0-255
    imagen_balance_blancos = cv2.cvtColor(imagen_lab, cv2.COLOR_LAB2BGR) # finalmente se convierte de nuevo a BGR

    # CLAHE en canal L para compensar iluminación no uniforme
    imagen_lab_clahe = cv2.cvtColor(imagen_balance_blancos, cv2.COLOR_BGR2LAB)
    canal_l, canal_a, canal_b = cv2.split(imagen_lab_clahe)
    ecualizador_clahe = cv2.createCLAHE(clipLimit=LIMITE_RECORTE_CLAHE, tileGridSize=TAMANO_CUADRICULA_CLAHE)
    canal_l_ecualizado = ecualizador_clahe.apply(canal_l)
    canales_combinados = cv2.merge([canal_l_ecualizado, canal_a, canal_b])
    imagen_normalizada = cv2.cvtColor(canales_combinados, cv2.COLOR_LAB2BGR)
    
    return imagen_normalizada


# ---------------------------------------------------------------------------
# Scores
# ---------------------------------------------------------------------------

############################### Centering ###############################

def calcular_score_centrado(
        imagen_corregida: np.ndarray,
        cuadrilatero: np.ndarray,
        forma_imagen_original: Tuple[int, int, int],
    ) -> float:
    """
    Mide el centrado comparando los márgenes reales de la carta dentro de
    la imagen original (distancia del quad a los bordes de la imagen).

    Score 100 → márgenes perfectamente iguales.
    Score 0   → carta completamente descentrada en al menos un eje.
    """

    alto_imagen_original, ancho_imagen_original = forma_imagen_original[:2]

    superior_izq, superior_der, inferior_der, inferior_izq = cuadrilatero

    # Márgenes (en cada lado) de la carta respecto a los bordes de la imagen original
    margen_izquierdo = float(min(superior_izq[0], inferior_izq[0]))
    margen_derecho = float(ancho_imagen_original - max(superior_der[0], inferior_der[0]))
    margen_superior = float(min(superior_izq[1], superior_der[1]))
    margen_inferior = float(alto_imagen_original - max(inferior_izq[1], inferior_der[1]))

    score_horizontal = calcular_score_eje(margen_izquierdo, margen_derecho)
    score_vertical = calcular_score_eje(margen_superior, margen_inferior)

    # Se promedia el score horizontal y vertical, y se asegura que esté dentro del rango permitido
    return round(float(np.clip((score_horizontal + score_vertical) / 2, PUNTAJE_MINIMO, PUNTAJE_MAXIMO)), 2)

def calcular_score_eje(margen_uno: float, margen_dos: float) -> float:
    """Calcula el score de centrado en un eje (horizontal o vertical)."""

    MARGEN_TOTAL_MINIMO_VALIDO = 1.0
    FACTOR_NORMALIZACION_EJE = 200

    suma_margenes = margen_uno + margen_dos # suma de los márgenes en el eje (esto es para normalizar el score)
    if suma_margenes < MARGEN_TOTAL_MINIMO_VALIDO:
        return float(PUNTAJE_MAXIMO)
    
    margen_menor = min(margen_uno, margen_dos)

    # Si los márgenes son iguales, el score es 100; si uno es mucho menor, el score se acerca a 0
    return (margen_menor / suma_margenes) * FACTOR_NORMALIZACION_EJE


############################### Corners ###############################

def calcular_score_esquinas(imagen_corregida: np.ndarray) -> float:
    """
    Evalúa el estado de las cuatro esquinas. Analiza la curvatura y nitidez del borde en cada región de esquina.
    """

    alto, ancho = imagen_corregida.shape[:2]
    tamano_esquina_px = int(min(alto, ancho) * TAMANO_ESQUINA) # dado en pixeles

    # Se extraen las regiones de esquina (top-left, top-right, bottom-left, bottom-right)
    regiones_esquinas = [
        imagen_corregida[0:tamano_esquina_px, 0:tamano_esquina_px],            # top-left
        imagen_corregida[0:tamano_esquina_px, ancho-tamano_esquina_px:ancho],  # top-right
        imagen_corregida[alto-tamano_esquina_px:alto, 0:tamano_esquina_px],   # bottom-left
        imagen_corregida[alto-tamano_esquina_px:alto, ancho-tamano_esquina_px:ancho],  # bottom-right
    ]

    puntajes = []
    # Se calcula el score de cada región de esquina
    for region_esquina in regiones_esquinas:
        puntajes.append(calcular_score_region_esquina(region_esquina))

    # Si el score es 100 quiere dedcir esquinas perfectas, si es 0 quiere decir esquinas muy dañadas, se hace un promedio
    return round(float(np.mean(puntajes)), 2)

def calcular_score_region_esquina(region_esquina: np.ndarray) -> float:
    """
    Puntúa una región de esquina. Detecta bordes con Canny, mide qué tan "recto" y nítido es el borde de la esquina.
    """

    UMBRAL_CANNY_INFERIOR = 50
    UMBRAL_CANNY_SUPERIOR = 150
    DIVISOR_BANDA_PERIMETRAL = 3   # ancho de la banda perimetral = 1/3 del lado de la región
    EPSILON_DIVISION = 1e-5
    LIMITE_NORMALIZADO_INFERIOR = 0
    LIMITE_NORMALIZADO_SUPERIOR = 1
    FACTOR_PORCENTAJE = 100

    imagen_gris  = cv2.cvtColor(region_esquina, cv2.COLOR_BGR2GRAY) # convertir a escala de grises para análisis de bordes
    imagen_bordes = cv2.Canny(imagen_gris, UMBRAL_CANNY_INFERIOR, UMBRAL_CANNY_SUPERIOR) # detectar bordes con Canny (canny es un algoritmo de detección de bordes)

    # Varianza local de la imagen → más textura inesperada = más daño
    varianza_laplaciano = cv2.Laplacian(imagen_gris, cv2.CV_64F).var()

    # Crear máscara para la banda perimetral de la esquina, quiere decir, la zona donde se espera que haya borde (la parte más externa de la esquina)
    mascara_esquina = np.zeros_like(imagen_bordes)
    alto_region, ancho_region = region_esquina.shape[:2]

    # Banda perimetral de la esquina
    mascara_esquina[:max(1, alto_region // DIVISOR_BANDA_PERIMETRAL), :] = 1 # se marca la franja superior
    mascara_esquina[:, :max(1, ancho_region // DIVISOR_BANDA_PERIMETRAL)] = 1 # se marca la franja izquierda

    # Densidad de borde en la zona de esquina vs. superficie
    densidad_borde_esquina = imagen_bordes[mascara_esquina == 1].mean()
    densidad_borde_superficie = imagen_bordes[mascara_esquina == 0].mean() if (mascara_esquina == 0).any() else 0

    # Alta densidad de borde en zona de esquina y baja en superficie → buena esquina
    relacion_densidad_bordes = densidad_borde_esquina / (densidad_borde_superficie + EPSILON_DIVISION)
    score_relacion = np.clip(relacion_densidad_bordes / TOLERANCIA_RATIO_ESQUINA, LIMITE_NORMALIZADO_INFERIOR, LIMITE_NORMALIZADO_SUPERIOR) * FACTOR_PORCENTAJE  # normalizar

    # Penalizar alta varianza Laplaciana (desgaste / arrugas)
    penalizacion_laplaciano = np.clip(varianza_laplaciano / TOLERANCIA_LAP_ESQUINA, LIMITE_NORMALIZADO_INFERIOR, LIMITE_NORMALIZADO_SUPERIOR) * PESO_LAP_ESQUINA  # hasta -30 pts

    return float(np.clip(score_relacion - penalizacion_laplaciano, PUNTAJE_MINIMO, PUNTAJE_MAXIMO))


################################ Bordes ################################

def calcular_score_bordes(imagen_corregida: np.ndarray) -> float:
    """
    Evalúa el estado de los cuatro bordes de la carta. 
    Mide la uniformidad y rectitud de las franjas perimetrales (las franjas perimetrales son las zonas más externas de la carta).
    """

    alto, ancho = imagen_corregida.shape[:2]
    grosor_borde_px = int(min(alto, ancho) * GROSOR_BORDE)

    franjas_borde = {
        "top":    imagen_corregida[0:grosor_borde_px, grosor_borde_px:ancho-grosor_borde_px],
        "bottom": imagen_corregida[alto-grosor_borde_px:alto, grosor_borde_px:ancho-grosor_borde_px],
        "left":   imagen_corregida[grosor_borde_px:alto-grosor_borde_px, 0:grosor_borde_px],
        "right":  imagen_corregida[grosor_borde_px:alto-grosor_borde_px, ancho-grosor_borde_px:ancho],
    }

    puntajes = []
    for nombre, franja in franjas_borde.items():
        puntajes.append(calcular_score_franja_borde(franja))

    # Si el score es 100 quiere decir bordes perfectos, si es 0 quiere decir bordes muy dañados, se hace un promedio
    return round(float(np.mean(puntajes)), 2)


def calcular_score_franja_borde(franja: np.ndarray) -> float:
    """
    Puntúa una franja de borde. Alta uniformidad de color significa borde limpio. Si hay ruido o irregularidades, se aplica una penalización.
    """

    LIMITE_NORMALIZADO_INFERIOR = 0
    LIMITE_NORMALIZADO_SUPERIOR = 1

    if franja.size == 0:
        return float(PUNTAJE_MAXIMO) # si la franja está vacía, se considera perfecta (no hay borde que evaluar)

    imagen_gris = cv2.cvtColor(franja, cv2.COLOR_BGR2GRAY)

    # Desviación estándar del brillo: alta quiere decir irregularidades
    desviacion_brillo = imagen_gris.std()

    # Varianza Laplaciana: alta quiere decir ruido o daño
    varianza_laplaciano = cv2.Laplacian(imagen_gris, cv2.CV_64F).var()

    # Score inversamente proporcional al ruido
    score_brillo = np.clip(1 - desviacion_brillo / TOLERANCIA_BRILLO_BORDE, LIMITE_NORMALIZADO_INFERIOR, LIMITE_NORMALIZADO_SUPERIOR) * PESO_BRILLO_BORDE
    score_laplaciano = np.clip(1 - varianza_laplaciano / TOLERANCIA_RUIDO_BORDE, LIMITE_NORMALIZADO_INFERIOR, LIMITE_NORMALIZADO_SUPERIOR) * PESO_RUIDO_BORDE

    return float(score_brillo + score_laplaciano)


############################### Superficie ###############################

def calcular_score_superficie(imagen_corregida: np.ndarray) -> float:
    """
    Evalúa la superficie central de la carta (excluyendo bordes y esquinas). Detecta rayones, marcas, pérdida de lustre y deformaciones.
    """

    TAMANO_KERNEL_DIFUMINADO = (31, 31) # cuando se dice kernel se refiere a la ventana de convolución para el filtro gaussiano
    CANAL_SATURACION_HSV = 1
    LIMITE_NORMALIZADO_INFERIOR = 0
    LIMITE_NORMALIZADO_SUPERIOR = 1

    alto, ancho = imagen_corregida.shape[:2]
    tamano_esquina_px = int(min(alto, ancho) * TAMANO_ESQUINA)
    grosor_borde_px = int(min(alto, ancho) * GROSOR_BORDE)
    margen_superficie = max(tamano_esquina_px, grosor_borde_px) # se define un margen para excluir esquinas y bordes

    region_superficie = imagen_corregida[margen_superficie:alto-margen_superficie, margen_superficie:ancho-margen_superficie]
    if region_superficie.size == 0:
        return float(PUNTAJE_MAXIMO)

    imagen_gris = cv2.cvtColor(region_superficie, cv2.COLOR_BGR2GRAY)

    # Detección de rayones (líneas finas de alto contraste) ---
    laplaciano = cv2.Laplacian(imagen_gris, cv2.CV_64F)
    varianza_laplaciano = laplaciano.var()

    # Uniformidad del brillo (manchas / sombras locales) ---
    imagen_difuminada   = cv2.GaussianBlur(imagen_gris, TAMANO_KERNEL_DIFUMINADO, 0)
    diferencia_difuminado = cv2.absdiff(imagen_gris, imagen_difuminada).astype(np.float32)
    densidad_manchas = diferencia_difuminado.mean()

    # Homogeneidad de color (fading / decoloración) ---
    imagen_hsv = cv2.cvtColor(region_superficie, cv2.COLOR_BGR2HSV)
    desviacion_saturacion = imagen_hsv[:, :, CANAL_SATURACION_HSV].astype(np.float32).std()

    # Pesos
    score_laplaciano = np.clip(1 - varianza_laplaciano / TOLERANCIA_LAP_SUPERFICIE, LIMITE_NORMALIZADO_INFERIOR, LIMITE_NORMALIZADO_SUPERIOR) * PESO_LAP_SUPERFICIE
    score_manchas = np.clip(1 - densidad_manchas / TOLERANCIA_MANCHAS_SUPERFICIE, LIMITE_NORMALIZADO_INFERIOR, LIMITE_NORMALIZADO_SUPERIOR) * PESO_MANCHAS_SUPERFICIE
    score_color = np.clip(1 - desviacion_saturacion / TOLERANCIA_COLOR_SUPERFICIE, LIMITE_NORMALIZADO_INFERIOR, LIMITE_NORMALIZADO_SUPERIOR) * PESO_COLOR_SUPERFICIE

    # Si el score es 100 quiere decir superficie perfecta, si es 0 quiere decir superficie muy dañada, se hace un promedio ponderado
    return round(float(score_laplaciano + score_manchas + score_color), 2)

