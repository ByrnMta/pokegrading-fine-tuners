import { postFormData } from '../solicitudes/api_client'

/**
 * Envía las imágenes de una carta para comparar contra la base de datos.
 *
 * El backend debe devolver hasta 3 candidatos similares con su metadata
 * y porcentaje de similitud.
 *
 * @param {FormData} formData - FormData con imagen frontal e imagen reverso.
 * @returns {Promise<{ok: boolean, data: any, status?: number, message?: string}>}
 */
export async function compareSubmitterCard(formData) {
    return postFormData('/submitter/compare', formData)
}

/**
 * Envía la carta final del flujo Submitter.
 *
 * Recibe las imágenes, la metadata editada y opcionalmente el card_id
 * del candidato seleccionado.
 *
 * @param {FormData} formData - FormData con imágenes, metadata y candidato seleccionado.
 * @returns {Promise<{ok: boolean, data: any, status?: number, message?: string}>}
 */
export async function createSubmitterCard(formData) {
    return postFormData('/submitter/cards', formData)
}