import {
    validateCardFile,
    validateSubmitterImages,
} from '../utils/validators/cards'

import { mockSubmitterCandidates } from '../utils/mocks/submitterCandidates'
import { SUBMITTER_USE_MOCK } from '../constants/submitter'

/**
 * Maneja la selección y validación individual de imágenes del flujo Submitter.
 *
 * @param {Object} params - Parámetros del handler.
 * @param {React.ChangeEvent<HTMLInputElement>} params.event - Evento del input file.
 * @param {'front' | 'back'} params.side - Lado de la imagen.
 * @param {(file: File|null) => void} params.setFrontFile - Setter de imagen frontal.
 * @param {(file: File|null) => void} params.setBackFile - Setter de imagen reverso.
 * @param {(callback: Function|Object) => void} params.setErrors - Setter de errores.
 * @returns {void}
 */
export function handleSubmitterFile({
    event,
    side,
    setFrontFile,
    setBackFile,
    setErrors,
}) {
    const file = event.target.files?.[0] || null
    const errorKey = side === 'front' ? 'imagen_frontal' : 'imagen_reverso'

    if (side === 'front') {
        setFrontFile(null)
    } else {
        setBackFile(null)
    }

    setErrors((currentErrors) => ({
        ...currentErrors,
        [errorKey]: undefined,
        compare: undefined,
        submit: undefined,
        success: undefined,
    }))

    if (!file) return

    const validation = validateCardFile(file)

    if (!validation.ok) {
        setErrors((currentErrors) => ({
            ...currentErrors,
            [errorKey]: validation.error,
        }))
        return
    }

    if (side === 'front') {
        setFrontFile(file)
    } else {
        setBackFile(file)
    }
}

/**
 * Abre la imagen seleccionada en una pestaña nueva.
 *
 * @param {Object} params - Parámetros del handler.
 * @param {'front' | 'back'} params.side - Lado de la imagen.
 * @param {File|null} params.frontFile - Imagen frontal.
 * @param {File|null} params.backFile - Imagen reverso.
 * @returns {void}
 */
export function handleOpenSubmitterImage({
    side,
    frontFile,
    backFile,
}) {
    const targetFile = side === 'front' ? frontFile : backFile

    if (!targetFile) return

    const url = URL.createObjectURL(targetFile)

    window.open(url, '_blank', 'noopener,noreferrer')
    setTimeout(() => URL.revokeObjectURL(url), 0)
}

/**
 * Construye el FormData para comparar una carta.
 *
 * @param {Object} params - Parámetros.
 * @param {File} params.frontFile - Imagen frontal.
 * @param {File} params.backFile - Imagen reverso.
 * @returns {FormData}
 */
export function buildSubmitterCompareFormData({
    frontFile,
    backFile,
}) {
    const fd = new FormData()

    fd.append('imagen_frontal', frontFile)
    fd.append('imagen_reverso', backFile)

    return fd
}

/**
 * Construye el FormData para crear/enviar una carta desde Submitter.
 *
 * Actualmente solo envía imágenes para que el backend procese la carta.
 *
 * @param {Object} params - Parámetros.
 * @param {File} params.frontFile - Imagen frontal.
 * @param {File} params.backFile - Imagen reverso.
 * @returns {FormData}
 */
export function buildSubmitterCreateFormData({
    frontFile,
    backFile,
}) {
    const fd = new FormData()

    fd.append('imagen_frontal', frontFile)
    fd.append('imagen_reverso', backFile)

    return fd
}

/**
 * Normaliza la respuesta de comparación del backend.
 *
 * Acepta distintos formatos posibles para evitar acoplar el frontend
 * demasiado pronto a una única forma de respuesta.
 *
 * @param {Object|Array} responseData - Data devuelta por el backend.
 * @returns {Array<Object>} Lista de candidatos.
 */
export function normalizeSubmitterCandidates(responseData) {
    if (Array.isArray(responseData)) {
        return responseData
    }

    if (Array.isArray(responseData?.candidatos)) {
        return responseData.candidatos
    }

    if (Array.isArray(responseData?.candidates)) {
        return responseData.candidates
    }

    if (Array.isArray(responseData?.results)) {
        return responseData.results
    }

    if (Array.isArray(responseData?.data?.candidatos)) {
        return responseData.data.candidatos
    }

    return []
}

/**
 * Ejecuta la comparación de la carta.
 *
 * Si SUBMITTER_USE_MOCK está en true, usa mockSubmitterCandidates
 * aunque exista compareCard.
 *
 * @param {Object} params - Parámetros del handler.
 * @param {File|null} params.frontFile - Imagen frontal.
 * @param {File|null} params.backFile - Imagen reverso.
 * @param {(formData: FormData) => Promise<Object>} [params.compareCard] - Función del hook Submitter.
 * @param {(errors: Object|Function) => void} params.setErrors - Setter de errores.
 * @param {(candidate: Object|null) => void} params.setSelectedCandidate - Setter de candidato seleccionado.
 * @param {(candidates: Array<Object>) => void} params.setCandidates - Setter de candidatos.
 * @param {(loading: boolean) => void} params.setCompareLoading - Setter de loading de comparación.
 * @returns {Promise<void>}
 */
export async function handleSubmitterCompare({
    frontFile,
    backFile,
    compareCard,
    setErrors,
    setSelectedCandidate,
    setCandidates,
    setCompareLoading,
}) {
    setErrors({})
    setSelectedCandidate(null)
    setCandidates([])

    const imageErrors = validateSubmitterImages(frontFile, backFile)

    if (Object.keys(imageErrors).length) {
        setErrors(imageErrors)
        return
    }

    setCompareLoading(true)

    try {
        const fd = buildSubmitterCompareFormData({
            frontFile,
            backFile,
        })

        if (SUBMITTER_USE_MOCK || !compareCard) {
            console.log('Comparación Submitter usando mock:', {
                fd,
                frontFile,
                backFile,
            })

            await new Promise((resolve) => setTimeout(resolve, 400))

            setCandidates(mockSubmitterCandidates)
            return
        }

        const response = await compareCard(fd)

        if (!response?.ok) {
            setErrors({
                compare:
                    response?.message ||
                    'No se pudo comparar la carta. Verifica que el endpoint de comparación esté disponible.',
            })
            return
        }

        const normalizedCandidates = normalizeSubmitterCandidates(response.data)

        setCandidates(normalizedCandidates)
    } catch (err) {
        setErrors({
            compare: 'Ocurrio un error inesperado al comparar la carta.',
        })
    } finally {
        setCompareLoading(false)
    }
}

/**
 * Maneja la selección visual de un candidato.
 *
 * La selección actualmente no afecta el envío final.
 *
 * @param {Object} params - Parámetros del handler.
 * @param {Object} params.candidate - Candidato seleccionado.
 * @param {(candidate: Object) => void} params.setSelectedCandidate - Setter de candidato seleccionado.
 * @param {(errors: Object|Function) => void} params.setErrors - Setter de errores.
 * @returns {void}
 */
export function handleSubmitterCandidateSelect({
    candidate,
    setSelectedCandidate,
    setErrors,
}) {
    setSelectedCandidate(candidate)

    setErrors((currentErrors) => ({
        ...currentErrors,
        metadata: undefined,
        submit: undefined,
        success: undefined,
    }))
}

/**
 * Convierte un candidato seleccionado en metadata editable.
 *
 * Se mantiene para una posible reactivación futura del formulario editable.
 *
 * @param {Object|null} candidate - Candidato seleccionado.
 * @returns {Object} Metadata normalizada.
 */
export function mapSubmitterCandidateToMetadata(candidate) {
    return {
        nombre: candidate?.nombre || candidate?.name || '',
        set_name: candidate?.set_name || candidate?.set || '',
        numero: candidate?.numero || candidate?.number || '',
        edicion: candidate?.edicion || candidate?.edition || '',
        idioma: candidate?.idioma || candidate?.language || '',
        acabado: candidate?.acabado || candidate?.finish || '',
        rareza: candidate?.rareza || candidate?.rarity || '',
        tipo: candidate?.tipo || candidate?.type || '',
        hp: candidate?.hp || '',
        ilustrador: candidate?.ilustrador || candidate?.illustrator || '',
        anio_impresion: candidate?.anio_impresion || candidate?.print_year || '',
    }
}

/**
 * Autorellena la metadata usando el candidato seleccionado.
 *
 * Se mantiene para una posible reactivación futura del formulario editable.
 *
 * @param {Object} params - Parámetros del handler.
 * @param {Object|null} params.selectedCandidate - Candidato seleccionado.
 * @param {(metadata: Object) => void} params.setMetadata - Setter de metadata.
 * @param {(errors: Object|Function) => void} params.setErrors - Setter de errores.
 * @returns {void}
 */
export function handleSubmitterAutofill({
    selectedCandidate,
    setMetadata,
    setErrors,
}) {
    if (!selectedCandidate) {
        setErrors((currentErrors) => ({
            ...currentErrors,
            metadata: 'Selecciona un candidato antes de autorellenar.',
        }))
        return
    }

    setMetadata(mapSubmitterCandidateToMetadata(selectedCandidate))

    setErrors((currentErrors) => ({
        ...currentErrors,
        metadata: undefined,
        submit: undefined,
        success: undefined,
    }))
}

/**
 * Maneja la edición manual de metadata.
 *
 * Se mantiene para una posible reactivación futura del formulario editable.
 *
 * @param {Object} params - Parámetros del handler.
 * @param {React.ChangeEvent<HTMLInputElement>} params.event - Evento del input.
 * @param {(callback: Function|Object) => void} params.setMetadata - Setter de metadata.
 * @param {(callback: Function|Object) => void} params.setErrors - Setter de errores.
 * @returns {void}
 */
export function handleSubmitterMetadataChange({
    event,
    setMetadata,
    setErrors,
}) {
    const { name, value } = event.target

    setMetadata((currentMetadata) => ({
        ...currentMetadata,
        [name]: value,
    }))

    setErrors((currentErrors) => ({
        ...currentErrors,
        [name]: undefined,
        submit: undefined,
        success: undefined,
    }))
}

/**
 * Maneja el envío final de la carta.
 *
 * Actualmente solo envía imagen frontal e imagen reverso.
 * Si SUBMITTER_USE_MOCK está en true, simula el envío aunque exista submitCard.
 *
 * @param {Object} params - Parámetros del handler.
 * @param {React.FormEvent<HTMLFormElement>} params.event - Evento submit.
 * @param {File|null} params.frontFile - Imagen frontal.
 * @param {File|null} params.backFile - Imagen reverso.
 * @param {(formData: FormData) => Promise<Object>} [params.submitCard] - Función del hook Submitter.
 * @param {(errors: Object|Function) => void} params.setErrors - Setter de errores.
 * @param {(loading: boolean) => void} params.setSubmitLoading - Setter de loading.
 * @returns {Promise<void>}
 */
export async function handleSubmitterSubmit({
    event,
    frontFile,
    backFile,
    submitCard,
    setErrors,
    setSubmitLoading,
}) {
    event.preventDefault()
    setErrors({})

    const imageErrors = validateSubmitterImages(frontFile, backFile)

    if (Object.keys(imageErrors).length) {
        setErrors(imageErrors)
        return
    }

    setSubmitLoading(true)

    try {
        const fd = buildSubmitterCreateFormData({
            frontFile,
            backFile,
        })

        if (SUBMITTER_USE_MOCK || !submitCard) {
            console.log('Envío Submitter usando mock:', {
                fd,
                frontFile,
                backFile,
            })

            await new Promise((resolve) => setTimeout(resolve, 400))

            setErrors({
                success: 'Carta lista para enviar. Prueba frontend completada.',
            })

            return
        }

        const response = await submitCard(fd)

        if (!response?.ok) {
            setErrors({
                submit:
                    response?.message ||
                    'No se pudo enviar la carta. Verifica que el endpoint de envío esté disponible.',
            })
            return
        }

        setErrors({
            success: 'Carta enviada correctamente.',
        })
    } catch (err) {
        setErrors({
            submit: 'Ocurrio un error inesperado al enviar la carta.',
        })
    } finally {
        setSubmitLoading(false)
    }
}