import { postCard } from '../../services/cards/api_cards'

const DEFAULT_ERROR = 'Error de validacion'

/**
 * Hook para gestionar las tarjetas
 * @returns {Object} Objeto con las propiedades y funciones relacionadas con las tarjetas.
 */
export default function useCards() {
    
    // Función para normalizar los errores de la respuesta del backend, los adapta a un formato consistente
    const normalizeErrors = (response, fallbackMessage) => {
        // Extrae el detalle del error según el formato de la respuesta
        const detail = response?.data?.detail
        // Si es un objeto se devuelve directamente
        if (detail && typeof detail === 'object') {
            return detail
        }
        return { submit: response?.message || fallbackMessage }
    }

    /**
     * Función para agregar una nueva tarjeta.
     *
     * @param {Object} formData - Datos del formulario de la tarjeta.
     * @returns {Promise<Object>} Respuesta de la solicitud.
     */
    const addCard = async (formData) => {
        // Llama al servicio para agregar una nueva tarjeta
        const response = await postCard(formData)
        // Si la respuesta no es ok, normaliza los errores y los devuelve
        if (!response.ok) {
            return { ok: false, errors: normalizeErrors(response, DEFAULT_ERROR) }
        }
        return { ok: true, data: response.data }
    }

    return { addCard }
}
