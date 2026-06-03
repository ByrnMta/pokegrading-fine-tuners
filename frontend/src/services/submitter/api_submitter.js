import { postFormData } from '../solicitudes/api_client'

/**
 * Compara una carta contra la base de datos.
 *
 * Endpoint real:
 * POST /submitter/buscar
 *
 * Campos FormData:
 * - imagen_frontal
 * - imagen_reverso
 * - top_k
 *
 * @param {FormData} formData
 * @returns {Promise<{ok: boolean, data: any, status?: number, message?: string}>}
 */
export async function compareSubmitterCard(formData) {
    return postFormData('/submitter/buscar', formData)
}

/**
 * Envía una carta para evaluación.
 *
 * Endpoint real:
 * POST /evaluacion-carta/enviar-evaluacion?id_usuario=1
 *
 * Campos FormData:
 * - toma_frontal
 * - toma_reversa
 *
 * @param {FormData} formData
 * @returns {Promise<{ok: boolean, data: any, status?: number, message?: string}>}
 */
export async function createSubmitterCard(formData) {
    return postFormData('/evaluacion-carta/enviar-evaluacion?id_usuario=1', formData)
}