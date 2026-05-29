const PASSWORD_MISMATCH_MESSAGE = 'Las contraseñas no coinciden'
const REQUIRED_MESSAGE = 'Requerido'

// Validación de confirmación de contraseña
export function validatePasswordConfirmation(password, confirmPassword) {
    if (password !== confirmPassword) {
        return { ok: false, error: PASSWORD_MISMATCH_MESSAGE }
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

    // Validación de confirmación de contraseña
    const passwordCheck = validatePasswordConfirmation(fields?.contrasena, fields?.confirm_password)
    if (!passwordCheck.ok) {
        err.confirm_password = passwordCheck.error
    }

    return err
}
