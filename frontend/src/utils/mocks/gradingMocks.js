/**
 * Mock de respuesta exitosa de POST /evaluacion-carta/enviar-evaluacion.
 *
 * El backend corre el pipeline completo (preprocesamiento + grading)
 * y devuelve el resultado final en una sola respuesta.
 */
export const mockSubmitWithGradingSuccess = {
    ok: true,
    data: {
        id_evaluacion: 'eval-mock-xyz789',
        version_algoritmo: 'pokegrading-v1.2.3',
        grado_final: 8.5,
        incertidumbre: 0.3,
        subgrades: {
            centering: 9.0,
            corners: 8.5,
            edges: 8.0,
            surface: 8.5,
        },
        baseline_usado: {
            tipo: 'calibrado',
            set_name: 'Base Set',
            acabado: 'Holo',
        },
    },
}

/**
 * Mock cuando no se puede aislar la carta del fondo (deriva a calificación manual).
 */
export const mockSubmitNoCardIsolated = {
    ok: false,
    status: 422,
    message: 'No se pudo aislar la carta del fondo. Será derivada a calificación manual.',
    data: {
        razon: 'no_card_isolated',
    },
}

/**
 * Mock cuando la imagen tiene distorsiones irrecuperables (pide recaptura).
 */
export const mockSubmitUncorrectableDistortion = {
    ok: false,
    status: 422,
    message: 'La imagen tiene distorsiones que no pueden corregirse. Por favor, recaptura la carta.',
    data: {
        razon: 'uncorrectable_distortion',
    },
}

/**
 * Mock cuando falta un subgrade (deriva a revisión humana).
 */
export const mockSubmitMissingSubgrade = {
    ok: false,
    status: 422,
    message: 'No se pudo calcular el subgrade de surface con insumos suficientes.',
    data: {
        razon: 'missing_subgrade',
        subgrade_faltante: 'surface',
    },
}

/**
 * Mock cuando hay incoherencia interna en los subgrades (deriva a revisión humana).
 */
export const mockSubmitCoherenceFailure = {
    ok: false,
    status: 422,
    message: 'El resultado contradice los umbrales mínimos de coherencia interna.',
    data: {
        razon: 'coherence_failure',
    },
}
