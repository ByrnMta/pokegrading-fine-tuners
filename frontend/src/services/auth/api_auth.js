import { postJson, getJson } from '../api_client'

/**
 * Inicia sesión con las credenciales proporcionadas.
 * @param {{correo: string, contrasena: string}} data
 */
export async function login(data) {
  return postJson('/usuario/login', data)
}

/**
 * Registra un nuevo usuario.
 * @param {{nombre_usuario: string, correo: string, contrasena: string}} data
 */
export async function register(data) {
  return postJson('/usuario/registro', data)
}

