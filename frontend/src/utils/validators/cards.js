export const ALLOWED_IMAGE_EXT = ['jpeg', 'png', 'heic']

const REQUIRED_MESSAGE = 'Requerido'
const IMAGE_FORMAT_MESSAGE = 'Formato no soportado. Use jpeg, png o heic.'

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
export function validateCardFields(form, file) {
    const err = {}

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
    if (!file) 
        err.imagen = REQUIRED_MESSAGE

    const fileValidation = validateCardFile(file)
    if (!fileValidation.ok) {
        err.imagen = fileValidation.error
    }

    return err
}
