from __future__ import annotations

import io
import math
from dataclasses import dataclass
from typing import Optional, Tuple
from fastapi import UploadFile

import cv2
import numpy as np
from skimage import exposure, filters

# ---------------------------------------------------------------------------
# Constantes de configuración
# ---------------------------------------------------------------------------

# Relación de aspecto estándar de una carta (Pokémon, MTG, TCG)
CARD_ASPECT_RATIO = 63.5 / 88.0          # ancho / alto  ≈ 0.721
ASPECT_RATIO_TOLERANCE = 0.12            # ±12 % de tolerancia

# Salida canónica en píxeles (útil para análisis reproducible)
CANONICAL_WIDTH  = 630
CANONICAL_HEIGHT = 880

# Grosor de cada región como fracción del lado correspondiente
CENTERING_BAND  = 0.08   # banda perimetral para medir bordes de centrado
CORNER_SIZE     = 0.12   # tamaño del cuadrado de esquina (fracción del lado corto)
EDGE_WIDTH      = 0.06   # grosor de la franja de borde (fracción del lado corto)

# Umbrales de descarte
MIN_CARD_AREA_FRACTION = 0.05   # la carta debe ocupar al menos el 5 % de la imagen
MAX_WARP_ANGLE_DEG     = 45.0   # ángulo máximo corregible; más distorsión irrecuperable

# Corners
CORNER_LAP_TOLERANCE   = 4000.0   # entre más alto más permisivo con desgaste
CORNER_LAP_WEIGHT      = 10.0    # entre más alto más penaliza el desgaste
CORNER_RATIO_TOLERANCE = 0.5     # entre más alto más permisivo con el filo

# Edges
EDGE_BRIGHTNESS_TOLERANCE = 800.0   # entre más alto más permisivo con variación de brillo
EDGE_BRIGHTNESS_WEIGHT    = 60.0   # peso del brillo en el score final
EDGE_LAP_TOLERANCE        = 1200.0  # entre más alto más permisivo con ruido
EDGE_LAP_WEIGHT           = 40.0   # peso del ruido en el score final

# Surface
SURFACE_LAP_TOLERANCE     = 8000.0  # entre más alto más permisivo con rayones
SURFACE_LAP_WEIGHT        = 35.0   # peso de rayones en el score final
SURFACE_SCRATCH_TOLERANCE = 100.0   # entre más alto más permisivo con manchas
SURFACE_SCRATCH_WEIGHT    = 35.0   # peso de manchas en el score final
SURFACE_COLOR_TOLERANCE   = 600.0   # entre más alto más permisivo con decoloración
SURFACE_COLOR_WEIGHT      = 30.0   # peso de decoloración en el score final


# ---------------------------------------------------------------------------
# Tipos internos
# ---------------------------------------------------------------------------

@dataclass
class CardContour:
    """Información del contorno detectado de la carta."""
    quad: np.ndarray          # 4 puntos (x, y) ordenados
    area: float
    angle_deg: float          # ángulo de inclinación estimado

@dataclass
class GradingResult:
    centering: Optional[float]
    corners:   Optional[float]
    edges:     Optional[float]
    surface:   Optional[float]


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def analizar_carta(image: UploadFile, errores: dict) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Recibe un UploadFile (imagen ya validada y limpia) y regresa (centering, corners, edges, surface) floats 0-100,
    o (None, None, None, None) si el procesamiento falla.

    Casos de retorno None:
        • No se pudo aislar la carta del fondo  → derivar a calificación manual.
        • Distorsión irrecuperable              → solicitar recaptura.
    """

    # 1. Leer bytes y decodificar la imagen
    image.file.seek(0)
    imagen_bytes = image.file.read()
    img_bgr = decodificar_imagen(imagen_bytes) # es un np.ndarray de OpenCV en formato BGR
    if img_bgr is None:
        errores["imagen"] = "No se pudo decodificar la imagen. Asegúrese de que sea un archivo de imagen válido."
        return None, None, None, None

    # 2. Detectar y aislar la carta
    card_contour = _detect_card_contour(img_bgr)
    if card_contour is None:
        print("analizar_carta: no se pudo aislar la carta del fondo: revisión manual.")
        return None, None, None, None

    # 3. Validar que la distorsión sea corregible
    if card_contour.angle_deg > MAX_WARP_ANGLE_DEG:
        errores["imagen"] = "Distorsión irrecuperable. Por favor, recapture la imagen."
        return None, None, None, None

    # 4. Corrección de perspectiva: imagen canónica de la carta
    warped = _correct_perspective(img_bgr, card_contour.quad)

    # 5. Normalizar color e iluminación
    normalized = _normalize_color(warped)

    # 6. Calcular scores
    centering = _score_centering(normalized, card_contour.quad, img_bgr.shape)
    corners   = _score_corners(normalized)
    edges     = _score_edges(normalized)
    surface   = _score_surface(normalized)

    print(f"analizar_carta: centering={centering}, corners={corners}, edges={edges}, surface={surface}")

    return centering, corners, edges, surface

# ---------------------------------------------------------------------------
# Paso 1 – Decodificación
# ---------------------------------------------------------------------------

def decodificar_imagen(data: bytes) -> Optional[np.ndarray]:
    """Convierte bytes en imagen BGR de OpenCV."""

    array_numpy = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(array_numpy, cv2.IMREAD_COLOR)
    return img  # None si falla

# ---------------------------------------------------------------------------
# Paso 2 – Detección de la carta
# ---------------------------------------------------------------------------

def _detect_card_contour(img: np.ndarray) -> Optional[CardContour]:
    """
    Intenta localizar el cuadrilátero de la carta en la imagen.
    Retorna None si no se encuentra un candidato válido.
    """
    h, w = img.shape[:2]
    img_area = h * w

    # Pre-procesamiento para detección de bordes
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur  = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 120)
    edges = cv2.dilate(edges, None, iterations=2)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Ordenar por área descendente y probar los mejores candidatos
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for cnt in contours[:8]:
        area = cv2.contourArea(cnt)
        if area < img_area * MIN_CARD_AREA_FRACTION:
            break  # los siguientes serán aún menores

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        if len(approx) != 4:
            continue

        quad = _order_points(approx.reshape(4, 2).astype(np.float32))

        # Validar relación de aspecto
        pw, ph = _quad_dimensions(quad)
        if ph == 0:
            continue
        ratio = pw / ph
        if abs(ratio - CARD_ASPECT_RATIO) > ASPECT_RATIO_TOLERANCE:
            # Intentar orientación vertical invertida
            if abs((ph / pw) - CARD_ASPECT_RATIO) <= ASPECT_RATIO_TOLERANCE:
                quad = _order_points(quad[[1, 2, 3, 0]])  # rotar puntos
                pw, ph = ph, pw
            else:
                continue

        angle = _estimate_tilt(quad)
        return CardContour(quad=quad, area=area, angle_deg=angle)

    return None  # ningún candidato válido


def _order_points(pts: np.ndarray) -> np.ndarray:
    """Ordena 4 puntos: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # TL
    rect[2] = pts[np.argmax(s)]   # BR
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # TR
    rect[3] = pts[np.argmax(diff)]  # BL
    return rect


def _quad_dimensions(quad: np.ndarray) -> Tuple[float, float]:
    """Ancho y alto aproximados del cuadrilátero."""
    tl, tr, br, bl = quad
    w = (np.linalg.norm(tr - tl) + np.linalg.norm(br - bl)) / 2
    h = (np.linalg.norm(bl - tl) + np.linalg.norm(br - tr)) / 2
    return float(w), float(h)


def _estimate_tilt(quad: np.ndarray) -> float:
    """Ángulo de inclinación en grados (respecto al eje horizontal)."""
    tl, tr = quad[0], quad[1]
    dx = tr[0] - tl[0]
    dy = tr[1] - tl[1]
    return abs(math.degrees(math.atan2(dy, dx)))


# ---------------------------------------------------------------------------
# Paso 3 – Corrección de perspectiva
# ---------------------------------------------------------------------------

def _correct_perspective(img: np.ndarray, quad: np.ndarray) -> np.ndarray:
    """
    Aplica transformación de perspectiva para obtener una vista frontal
    de la carta con tamaño canónico CANONICAL_WIDTH × CANONICAL_HEIGHT.
    """
    dst = np.array([
        [0,                  0],
        [CANONICAL_WIDTH - 1, 0],
        [CANONICAL_WIDTH - 1, CANONICAL_HEIGHT - 1],
        [0,                  CANONICAL_HEIGHT - 1],
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(quad, dst)
    warped = cv2.warpPerspective(img, M, (CANONICAL_WIDTH, CANONICAL_HEIGHT))
    return warped

# ---------------------------------------------------------------------------
# Paso 4 – Normalización de color e iluminación
# ---------------------------------------------------------------------------

def _normalize_color(img: np.ndarray) -> np.ndarray:
    """
    Normaliza la iluminación con CLAHE en el canal L (Lab)
    y ajusta el balance de blancos con corrección de escala de grises.
    """
    # Balance de blancos (escala de grises simple)
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    avg_a = np.mean(result[:, :, 1])
    avg_b = np.mean(result[:, :, 2])
    result[:, :, 1] -= (avg_a - 128)
    result[:, :, 2] -= (avg_b - 128)
    result = np.clip(result, 0, 255).astype(np.uint8)
    img_wb = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

    # CLAHE en canal L para compensar iluminación no uniforme
    lab  = cv2.cvtColor(img_wb, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_eq  = clahe.apply(l)
    merged = cv2.merge([l_eq, a, b])
    normalized = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    return normalized


# ---------------------------------------------------------------------------
# Paso 5 – Scores
# ---------------------------------------------------------------------------

# ── 5.1  Centering ──────────────────────────────────────────────────────────

def _score_centering(
    warped: np.ndarray,
    quad: np.ndarray,
    orig_shape: Tuple[int, int, int],
) -> float:
    """
    Mide el centrado comparando los márgenes reales de la carta dentro de
    la imagen original (distancia del quad a los bordes de la imagen).

    Score 100 → márgenes perfectamente iguales.
    Score 0   → carta completamente descentrada en al menos un eje.
    """
    h_img, w_img = orig_shape[:2]

    tl, tr, br, bl = quad

    # Márgenes en cada lado
    left   = float(min(tl[0], bl[0]))
    right  = float(w_img - max(tr[0], br[0]))
    top    = float(min(tl[1], tr[1]))
    bottom = float(h_img - max(bl[1], br[1]))

    # Evitar división por cero
    def axis_score(a: float, b: float) -> float:
        total = a + b
        if total < 1:
            return 100.0
        smaller = min(a, b)
        return (smaller / total) * 200  # 50 % = perfecto → score 100

    h_score = axis_score(left, right)
    v_score = axis_score(top, bottom)

    return round(float(np.clip((h_score + v_score) / 2, 0, 100)), 2)


# ── 5.2  Corners ────────────────────────────────────────────────────────────

def _score_corners(warped: np.ndarray) -> float:
    """
    Evalúa el estado de las cuatro esquinas.
    Analiza la curvatura y nitidez del borde en cada región de esquina.

    Score 100 → esquinas perfectamente angulosas y limpias.
    Score 0   → esquinas muy dobladas o desgastadas.
    """
    h, w = warped.shape[:2]
    cs = int(min(h, w) * CORNER_SIZE)

    corners_regions = [
        warped[0:cs,      0:cs],       # TL
        warped[0:cs,      w-cs:w],     # TR
        warped[h-cs:h,    0:cs],       # BL
        warped[h-cs:h,    w-cs:w],     # BR
    ]

    scores = []
    for region in corners_regions:
        scores.append(_corner_region_score(region))

    return round(float(np.mean(scores)), 2)


def _corner_region_score(region: np.ndarray) -> float:
    """
    Puntúa una región de esquina.
    - Detecta bordes con Canny.
    - Mide qué tan "recto" y nítido es el borde de la esquina.
    - Un ángulo recto perfecto → 100; esquina redondeada/doblada → menor score.
    """
    gray  = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # Varianza local de la imagen → más textura inesperada = más daño
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Contornos en el borde: si hay pocos píxeles de borde, la esquina es limpia
    edge_density = edges.mean()  # 0-255 promediado como float

    # Score simple: un borde bien definido y poco ruido interno
    # edge_density alta en la periferia correcta es buena; ruido interno es malo
    corner_mask = np.zeros_like(edges)
    h, w = region.shape[:2]
    # Banda perimetral de la esquina
    corner_mask[:max(1, h//3), :] = 1
    corner_mask[:, :max(1, w//3)] = 1

    edge_in_corner  = edges[corner_mask == 1].mean()
    edge_in_surface = edges[corner_mask == 0].mean() if (corner_mask == 0).any() else 0

    # Alta densidad de borde en zona de esquina y baja en superficie → buena esquina
    ratio = edge_in_corner / (edge_in_surface + 1e-5)
    ratio_score = np.clip(ratio / CORNER_RATIO_TOLERANCE, 0, 1) * 100  # normalizar

    # Penalizar alta varianza Laplaciana (desgaste / arrugas)
    lap_penalty = np.clip(lap_var / CORNER_LAP_TOLERANCE, 0, 1) * CORNER_LAP_WEIGHT  # hasta -30 pts

    return float(np.clip(ratio_score - lap_penalty, 0, 100))


# ── 5.3  Edges ──────────────────────────────────────────────────────────────

def _score_edges(warped: np.ndarray) -> float:
    """
    Evalúa el estado de los cuatro bordes de la carta.
    Mide la uniformidad y rectitud de las franjas perimetrales.

    Score 100 → bordes perfectamente rectos y sin daño.
    Score 0   → bordes muy irregulares o desgastados.
    """
    h, w = warped.shape[:2]
    ew = int(min(h, w) * EDGE_WIDTH)

    edge_strips = {
        "top":    warped[0:ew,     ew:w-ew],
        "bottom": warped[h-ew:h,   ew:w-ew],
        "left":   warped[ew:h-ew,  0:ew],
        "right":  warped[ew:h-ew,  w-ew:w],
    }

    scores = []
    for name, strip in edge_strips.items():
        scores.append(_edge_strip_score(strip))

    return round(float(np.mean(scores)), 2)


def _edge_strip_score(strip: np.ndarray) -> float:
    """
    Puntúa una franja de borde.
    - Alta uniformidad de color → borde limpio.
    - Ruido / irregularidades → penalización.
    """
    if strip.size == 0:
        return 100.0

    gray = cv2.cvtColor(strip, cv2.COLOR_BGR2GRAY)

    # Desviación estándar del brillo: alta → irregularidades
    std_brightness = gray.std()

    # Varianza Laplaciana: alta → ruido / daño
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Score inversamente proporcional al ruido
    brightness_score = np.clip(1 - std_brightness / EDGE_BRIGHTNESS_TOLERANCE, 0, 1) * 60
    lap_score        = np.clip(1 - lap_var / EDGE_LAP_TOLERANCE, 0, 1) * EDGE_LAP_WEIGHT

    return float(brightness_score + lap_score)


# ── 5.4  Surface ────────────────────────────────────────────────────────────

def _score_surface(warped: np.ndarray) -> float:
    """
    Evalúa la superficie central de la carta (excluyendo bordes y esquinas).
    Detecta rayones, marcas, pérdida de lustre y deformaciones.

    Score 100 → superficie perfecta, sin defectos visibles.
    Score 0   → superficie muy dañada.
    """
    h, w = warped.shape[:2]
    cs = int(min(h, w) * CORNER_SIZE)
    ew = int(min(h, w) * EDGE_WIDTH)
    margin = max(cs, ew)

    surface_roi = warped[margin:h-margin, margin:w-margin]
    if surface_roi.size == 0:
        return 100.0

    gray = cv2.cvtColor(surface_roi, cv2.COLOR_BGR2GRAY)

    # --- Detección de rayones (líneas finas de alto contraste) ---
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap_var = lap.var()

    # --- Uniformidad del brillo (manchas / sombras locales) ---
    blur    = cv2.GaussianBlur(gray, (31, 31), 0)
    diff    = cv2.absdiff(gray, blur).astype(np.float32)
    scratch_density = diff.mean()

    # --- Homogeneidad de color (fading / decoloración) ---
    hsv = cv2.cvtColor(surface_roi, cv2.COLOR_BGR2HSV)
    sat_std = hsv[:, :, 1].astype(np.float32).std()

    # Pesos
    lap_score     = np.clip(1 - lap_var / SURFACE_LAP_TOLERANCE,       0, 1) * SURFACE_LAP_WEIGHT
    scratch_score = np.clip(1 - scratch_density / SURFACE_SCRATCH_TOLERANCE, 0, 1) * SURFACE_SCRATCH_WEIGHT
    color_score   = np.clip(1 - sat_std / SURFACE_COLOR_TOLERANCE,         0, 1) * SURFACE_COLOR_WEIGHT

    return round(float(lap_score + scratch_score + color_score), 2)

