import { postJson, getJson } from '../api_client'

/**
 * Inicia sesión con las credenciales proporcionadas.
 * @param {{email: string, password: string}} data
 */
export async function login(data) {
  return postJson('/login', data)
}

/**
 * Registra un nuevo usuario.
 * @param {{email: string, username: string, password: string}} data
 */
export async function register(data) {
  return postJson('/register', data)
}

