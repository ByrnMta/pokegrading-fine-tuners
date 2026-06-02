// ====== Constantes de validación
export const REGISTER_COUNTRIES = ['CR', 'PA', 'MX', 'CO', 'CL', 'AR']
export const REGISTER_LANGUAGES = ['es', 'en']
const BLOCKED_EMAIL_DOMAINS = ['mailinator.com', 'tempmail.com', '10minutemail.com']
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const MIN_PASSWORD_LENGTH = 8


// ====== Mensajes de error
const REQUIRED_MESSAGE = 'Requerido'
const PASSWORD_MISMATCH_MESSAGE = 'Las contraseñas no coinciden'
const INVALID_EMAIL_MESSAGE = 'Formato de correo invalido'
const BLOCKED_DOMAIN_MESSAGE = 'Dominio de correo no permitido'
const PASSWORD_RULES_MESSAGE = 'La contrasena debe tener al menos 8 caracteres, 1 mayuscula y 1 digito'
const INVALID_COUNTRY_MESSAGE = 'Pais no soportado'
const DISCLOSURE_REQUIRED_MESSAGE = 'Debes aceptar el disclosure'
const INVALID_LANGUAGE_MESSAGE = 'Idioma no valido'


// ====== Validaciones
// Validación de confirmación de contraseña
export function validatePasswordConfirmation(password, confirmPassword) {
    if (password !== confirmPassword) {
        return { ok: false, error: PASSWORD_MISMATCH_MESSAGE }
    }
    return { ok: true }
}

// Función para verificar si el dominio del correo está bloqueado
function isEmailBlocked(email) {
    const domain = email?.split('@')[1]?.toLowerCase()
    if (!domain) return false
    return BLOCKED_EMAIL_DOMAINS.includes(domain)
}

// Validación de reglas de contraseña (longitud mínima, mayúscula y dígito)
function validatePasswordRules(password) {
    const hasMinLength = password?.length >= MIN_PASSWORD_LENGTH
    const hasUppercase = /[A-Z]/.test(password || '')
    const hasDigit = /\d/.test(password || '')

    if (!hasMinLength || !hasUppercase || !hasDigit) {
        return { ok: false, error: PASSWORD_RULES_MESSAGE }
    }
    return { ok: true }
}

// Validación de campos del formulario de registro
export function validateRegisterFields(fields) {
    const err = {}

    if (!fields?.correo) 
        err.correo = REQUIRED_MESSAGE
    if (!fields?.nombre_usuario) 
        err.nombre_usuario = REQUIRED_MESSAGE
    if (!fields?.contrasena) 
        err.contrasena = REQUIRED_MESSAGE
    if (!fields?.confirm_password) 
        err.confirm_password = REQUIRED_MESSAGE
    if (!fields?.pais)
        err.pais = REQUIRED_MESSAGE
    if (!fields?.idioma)
        err.idioma = REQUIRED_MESSAGE
    if (!fields?.disclosure)
        err.disclosure = DISCLOSURE_REQUIRED_MESSAGE

    if (fields?.correo && !EMAIL_REGEX.test(fields.correo)) {
        err.correo = INVALID_EMAIL_MESSAGE
    } else if (fields?.correo && isEmailBlocked(fields.correo)) {
        err.correo = BLOCKED_DOMAIN_MESSAGE
    }

    // Validación de reglas de contraseña
    if (fields?.contrasena) {
        const passwordRules = validatePasswordRules(fields.contrasena)
        if (!passwordRules.ok) {
            err.contrasena = passwordRules.error
        }
    }

    // Validación de país e idioma contra listas permitidas
    if (fields?.pais && !REGISTER_COUNTRIES.includes(fields.pais)) {
        err.pais = INVALID_COUNTRY_MESSAGE
    }

    // Validación de idioma contra lista permitida
    if (fields?.idioma && !REGISTER_LANGUAGES.includes(fields.idioma)) {
        err.idioma = INVALID_LANGUAGE_MESSAGE
    }

    // Validación de confirmación de contraseña
    const passwordCheck = validatePasswordConfirmation(fields?.contrasena, fields?.confirm_password)
    if (!passwordCheck.ok) {
        err.confirm_password = passwordCheck.error
    }

    return err
}
