/**
 * Estados posibles del resultado de grading tras enviar la carta.
 */
export const GRADING_STATUS = {
    DONE: 'done',
    MANUAL_REVIEW: 'manual_review',
    RECAPTURE: 'recapture',
}

/**
 * Razones de derivación devueltas por el backend.
 */
export const GRADING_DERIVATION_REASON = {
    NO_CARD_ISOLATED: 'no_card_isolated',
    UNCORRECTABLE_DISTORTION: 'uncorrectable_distortion',
    MISSING_SUBGRADE: 'missing_subgrade',
    COHERENCE_FAILURE: 'coherence_failure',
}

/**
 * Etiquetas legibles para cada dimensión de subgrade.
 */
export const SUBGRADE_LABELS = {
    centering: 'Centering',
    corners: 'Corners',
    edges: 'Edges',
    surface: 'Surface',
}

/**
 * Orden canónico de los subgrades para visualización.
 */
export const SUBGRADE_ORDER = ['centering', 'corners', 'edges', 'surface']
