import {
    compareSubmitterCard,
    createSubmitterCard,
} from '../../services/submitter/api_submitter'

/**
 * Hook para centralizar las operaciones del flujo Submitter.
 *
 * Expone funciones listas para que los componentes o handlers puedan:
 * - comparar una carta contra la base de datos
 * - crear/enviar una carta desde el flujo Submitter
 *
 * @returns {{
 *   compareCard: (formData: FormData) => Promise<Object>,
 *   submitCard: (formData: FormData) => Promise<Object>
 * }}
 */
export default function useSubmitterCards() {
    /**
     * Compara una carta enviada por Submitter.
     *
     * @param {FormData} formData - Imágenes frontal y reverso.
     * @returns {Promise<Object>} Respuesta normalizada del backend.
     */
    const compareCard = async (formData) => {
        return compareSubmitterCard(formData)
    }

    /**
     * Envía la carta final del flujo Submitter.
     *
     * @param {FormData} formData - Imágenes, metadata y candidato seleccionado.
     * @returns {Promise<Object>} Respuesta normalizada del backend.
     */
    const submitCard = async (formData) => {
        return createSubmitterCard(formData)
    }

    return {
        compareCard,
        submitCard,
    }
}