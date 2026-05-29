import { postFormData } from '../solicitudes/api_client'

/**
 * Envía los datos de una nueva carta al servidor
 * @param {Object} formData - Los datos del formulario de la carta
 * @returns {Promise} - Una promesa que se resuelve con la respuesta del servidor
 */
export async function postCard(formData) {
    return postFormData('/catalogo/carta', formData)
}
