/**
 * Mock - Escenario 1: AUTO
 * Todo funciona, calificación completada automáticamente.
 */
export const mockSubmitWithGradingSuccess = {
    ok: true,
    data: {
        mensaje: 'Evaluacion de carta registrada exitosamente.',
        evaluacion: {
            id: 42,
            estado: 'COMPLETADA',
            tipo_revision: 'AUTO',
            requiere_accion: false,
        },
        calificacion: {
            version_algoritmo: '1.0.0',
            centering_subgrade: 8.3,
            corners_subgrade: 7.2,
            edges_subgrade: 8.8,
            surface_subgrade: 8.6,
            grado_final: 7.7,
            uncertainty_band: 0.3,
            baseline_origen: 'SET_ACABADO',
            tipo_revision: 'AUTO',
            coherence_flag: 'OK',
        },
    },
}

/**
 * Mock - Escenario 2: REVIEW
 * Calificación completada pero con incoherencia interna → revisión humana.
 */
export const mockSubmitReview = {
    ok: true,
    data: {
        mensaje: 'La calificacion se completo, pero los resultados presentan incoherencias internas y han sido derivados a revision humana. Te notificaremos la resolucion.',
        evaluacion: {
            id: 42,
            estado: 'REVIEW',
            tipo_revision: 'REVIEW',
            requiere_accion: true,
        },
        calificacion: {
            version_algoritmo: '1.0.0',
            centering_subgrade: 9.3,
            corners_subgrade: 9.5,
            edges_subgrade: 4.8,
            surface_subgrade: 9.2,
            grado_final: 5.3,
            uncertainty_band: 0.3,
            baseline_origen: 'GLOBAL',
            tipo_revision: 'REVIEW',
            coherence_flag: 'REVIEW',
        },
    },
}

/**
 * Mock — Escenario 3: MANUAL ✋
 * No se pudo calcular alguna dimensión → derivación a calificación manual.
 * calificacion es null.
 */
export const mockSubmitManual = {
    ok: true,
    data: {
        mensaje: 'No fue posible calcular algunos subgrades de forma automatica. La carta ha sido derivada a calificacion manual. Te notificaremos cuando este lista.',
        evaluacion: {
            id: 42,
            estado: 'MANUAL',
            tipo_revision: 'MANUAL',
            requiere_accion: true,
        },
        calificacion: null,
    },
}

/**
 * Mock — Escenario 4: IDEMPOTENCIA ♻️
 * Mismo id_sesion ya procesado; retorna el resultado anterior.
 */
export const mockSubmitIdempotent = {
    ok: true,
    data: {
        mensaje: 'Esta sesion ya fue procesada.',
        evaluacion: {
            id: 42,
            estado: 'COMPLETADA',
        },
        calificacion: {
            version_algoritmo: '1.0.0',
            centering_subgrade: 8.3,
            corners_subgrade: 7.2,
            edges_subgrade: 8.8,
            surface_subgrade: 8.6,
            grado_final: 7.7,
            uncertainty_band: 0.3,
            baseline_origen: 'SET_ACABADO',
            tipo_revision: 'AUTO',
            coherence_flag: 'OK',
        },
    },
}

/**
 * Mock - Escenario 5: ERROR
 * Validaciones previas fallaron (ej. imagen demasiado grande).
 */
export const mockSubmitError = {
    ok: false,
    status: 422,
    data: {
        errores: {
            'imagen tamaño': 'El tamaño de la imagen no debe exceder los 10MB.',
        },
    },
}
