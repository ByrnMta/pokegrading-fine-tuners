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
        const res = await api_auth.login(credentials)
        if (res.user) {
            set_user(res.user)
            localStorage.setItem(STORAGE_KEY, JSON.stringify(res.user))
        }
        return res
    }

    /**
     * Función para registrar un nuevo usuario.
     *
     * @param {Object} data - Datos del nuevo usuario.
     * @returns {Promise<Object>} Respuesta de la solicitud.
     */
    const register = async (data) => {
        const res = await api_auth.register(data)
        if (res.user) {
            set_user(res.user)
            localStorage.setItem(STORAGE_KEY, JSON.stringify(res.user))
        }
        return res
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