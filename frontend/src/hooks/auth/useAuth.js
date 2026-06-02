import { useEffect, useState } from 'react'
import * as api_auth from '../../services/auth/api_auth'

const STORAGE_KEY = 'auth_user'

/**
 * Hook para gestionar la autenticación del usuario
 * Es un wrapper de las funciones de login, registro y logout, además maneja la persistencia del usuario en localStorage
 *
 * @returns {Object} Objeto con las propiedades y funciones relacionadas con la autenticación.
 */
export default function useAuth() {
    const [user, set_user] = useState(null)

    // Función para normalizar los errores de la respuesta del backend, los adapta a un formato consistente
    const normalizeErrors = (response, fallbackMessage) => {
        // Extrae el detalle del error según el formato de la respuesta
        const detail = response?.data?.detail
        // Si es un objeto se devuelve directamente
        if (detail && typeof detail === 'object') {
            return detail
        }
        // Si es una cadena, se asigna al error del formulario
        return { form: response?.message || fallbackMessage }
    }

    // Intenta cargar el usuario para mantener la sesión activa
    useEffect(() => {
        // Al montar el hook, se intenta cargar el usuario desde localStorage
        const raw = localStorage.getItem(STORAGE_KEY)
        // Si hay datos, se parsean y se establecen en el estado. Si el parseo falla, se limpia localStorage.
        if (raw) {
            try {
                set_user(JSON.parse(raw))
            } catch {
                localStorage.removeItem(STORAGE_KEY)
            }
        }
    }, [])

    /**
     * Función para iniciar sesión.
     *
     * @param {Object} credentials - Credenciales de inicio de sesión.
     * @returns {Promise<Object>} Respuesta de la solicitud.
     */
    const login = async (credentials) => {
        // Llama al servicio de autenticación para iniciar sesión
        const response = await api_auth.login(credentials)
        // Si la respuesta no es ok, normaliza los errores y los devuelve
        if (!response.ok) {
            return { ok: false, errors: normalizeErrors(response, 'Error en el inicio de sesion') }
        }
        // Si la respuesta es ok se establece el estado y se guarda en localStorage para persistencia
        if (response.data?.user) {
            set_user(response.data.user)
            localStorage.setItem(STORAGE_KEY, JSON.stringify(response.data.user))
        }
        return { ok: true, data: response.data }
    }

    /**
     * Función para registrar un nuevo usuario.
     *
     * @param {Object} data - Datos del nuevo usuario.
     * @returns {Promise<Object>} Respuesta de la solicitud.
     */
    const register = async (data) => {
        // Llama al servicio de autenticación para registrar un nuevo usuario
        const response = await api_auth.register(data)
        // Si la respuesta no es ok, normaliza los errores y los devuelve
        if (!response.ok) {
            return { ok: false, errors: normalizeErrors(response, 'Error al registrar la cuenta') }
        }
        // Si la respuesta es ok se establece el estado y se guarda en localStorage para persistencia
        if (response.data?.user) {
            set_user(response.data.user)
            localStorage.setItem(STORAGE_KEY, JSON.stringify(response.data.user))
        }
        return { ok: true, data: response.data }
    }

    /**
     * Función para cerrar sesión.
     * Limpia el estado del usuario y elimina los datos de localStorage.
     */
    const logout = () => {
        set_user(null)
        localStorage.removeItem(STORAGE_KEY)
    }

    // Se retorna el estado del usuario y las funciones de autenticación
    return { user, login, register, logout }
}