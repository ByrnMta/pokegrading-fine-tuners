// ====== Constantes de validación
export const ALLOWED_IMAGE_EXT = ['jpeg', 'png', 'heic']
export const SUPPORTED_LANGUAGES = ['es', 'en', 'jp', 'pt', 'fr', 'de', 'it']
export const CANONICAL_RARITIES = [
    'common',
    'uncommon',
    'rare',
    'holo rare',
    'ultra rare',
    'secret rare'
]
export const VALID_TYPES = [
    'grass',
    'fire',
    'water',
    'lightning',
    'psychic',
    'fighting',
    'darkness',
    'metal',
    'fairy',
    'dragon',
    'colorless',
    'normal'
]


// ====== Mensajes de error
const REQUIRED_MESSAGE = 'Requerido'
const IMAGE_FORMAT_MESSAGE = 'Formato no soportado. Use jpeg, png o heic.'
const HP_NUMERIC_MESSAGE = 'HP debe ser numerico'
const INVALID_RARITY_MESSAGE = 'Rareza no valida'
const INVALID_TYPE_MESSAGE = 'Tipo no valido'
const INVALID_LANGUAGE_MESSAGE = 'Idioma no soportado'


// ====== Validaciones
// Función para extraer la extensión de un archivo
export function getFileExtension(name) {
    return String(name).split('.').pop().toLowerCase()
}

// Validación del archivo de imagen para la carta
export function validateCardFile(file) {
    if (!file) {
        return { ok: true }
    }

    // Validar que el archivo tenga una extensión permitida
    const ext = getFileExtension(file.name)
    if (!ALLOWED_IMAGE_EXT.includes(ext)) {
        return { ok: false, error: IMAGE_FORMAT_MESSAGE }
    }

    return { ok: true }
}

// Validación de campos del formulario de carta
export function validateCardFields(form, frontFile, backFile) {
    const err = {}

    // Normalización de campos para validaciones específicas
    const rarity = String(form?.rareza || '').trim().toLowerCase()
    const tipo = String(form?.tipo || '').trim().toLowerCase()
    const idioma = String(form?.idioma || '').trim().toLowerCase()

    // Validación de campos requeridos
    if (!form?.set_name) 
        err.set_name = REQUIRED_MESSAGE
    if (!form?.numero) 
        err.numero = REQUIRED_MESSAGE
    if (!form?.edicion) 
        err.edicion = REQUIRED_MESSAGE
    if (!form?.idioma) 
        err.idioma = REQUIRED_MESSAGE
    if (!form?.acabado) 
        err.acabado = REQUIRED_MESSAGE
    if (!form?.autor)
        err.autor = REQUIRED_MESSAGE
    if (!frontFile) 
        err.imagen_frontal = REQUIRED_MESSAGE
    if (!backFile)
        err.imagen_reverso = REQUIRED_MESSAGE

    // Validación de HP numérico (si se proporciona)
    if (form?.hp && !/^\d+$/.test(String(form.hp))) {
        err.hp = HP_NUMERIC_MESSAGE
    }

    // Validación de rareza, tipo e idioma contra listas permitidas
    if (rarity && !CANONICAL_RARITIES.includes(rarity)) {
        err.rareza = INVALID_RARITY_MESSAGE
    }

    // Validación de tipo contra lista permitida
    if (tipo && !VALID_TYPES.includes(tipo)) {
        err.tipo = INVALID_TYPE_MESSAGE
    }

    // Validación de idioma contra lista permitida
    if (idioma && !SUPPORTED_LANGUAGES.includes(idioma)) {
        err.idioma = INVALID_LANGUAGE_MESSAGE
    }

    // Validación del archivo de imagen del frente
    const frontValidation = validateCardFile(frontFile)
    if (!frontValidation.ok) {
        err.imagen_frontal = frontValidation.error
    }

    // Validación del archivo de imagen del reverso
    const backValidation = validateCardFile(backFile)
    if (!backValidation.ok) {
        err.imagen_reverso = backValidation.error
    }

    return err
}

// Validación de imágenes para el flujo Submitter.
// En Submitter tanto la imagen frontal como la del reverso son obligatorias.
export function validateSubmitterImages(frontFile, backFile) {
    const err = {}

    if (!frontFile) {
        err.imagen_frontal = REQUIRED_MESSAGE
    }

    if (!backFile) {
        err.imagen_reverso = REQUIRED_MESSAGE
    }

    const frontValidation = validateCardFile(frontFile)
    if (!frontValidation.ok) {
        err.imagen_frontal = frontValidation.error
    }

    const backValidation = validateCardFile(backFile)
    if (!backValidation.ok) {
        err.imagen_reverso = backValidation.error
    }

    return err
}

// Validación de metadata editable para el flujo Submitter.
// Se usa antes del envío final, no necesariamente antes de comparar.
export function validateSubmitterMetadata(metadata) {
    const err = {}

    const rarity = String(metadata?.rareza || '').trim().toLowerCase()
    const tipo = String(metadata?.tipo || '').trim().toLowerCase()
    const idioma = String(metadata?.idioma || '').trim().toLowerCase()

    if (!metadata?.nombre) {
        err.nombre = REQUIRED_MESSAGE
    }

    if (!metadata?.set_name) {
        err.set_name = REQUIRED_MESSAGE
    }

    if (!metadata?.numero) {
        err.numero = REQUIRED_MESSAGE
    }

    if (!metadata?.edicion) {
        err.edicion = REQUIRED_MESSAGE
    }

    if (!metadata?.idioma) {
        err.idioma = REQUIRED_MESSAGE
    }

    if (!metadata?.acabado) {
        err.acabado = REQUIRED_MESSAGE
    }

    if (metadata?.hp && !/^\d+$/.test(String(metadata.hp))) {
        err.hp = HP_NUMERIC_MESSAGE
    }

    if (metadata?.anio_impresion && !/^\d+$/.test(String(metadata.anio_impresion))) {
        err.anio_impresion = YEAR_NUMERIC_MESSAGE
    }

    if (rarity && !CANONICAL_RARITIES.includes(rarity)) {
        err.rareza = INVALID_RARITY_MESSAGE
    }

    if (tipo && !VALID_TYPES.includes(tipo)) {
        err.tipo = INVALID_TYPE_MESSAGE
    }

    if (idioma && !SUPPORTED_LANGUAGES.includes(idioma)) {
        err.idioma = INVALID_LANGUAGE_MESSAGE
    }

    return err
}
