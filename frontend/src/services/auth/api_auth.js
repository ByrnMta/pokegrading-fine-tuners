import { postJson, getJson } from '../solicitudes/api_client'

/**
 * Inicia sesión con las credenciales proporcionadas.
 * @param {{correo: string, contrasena: string}} data
 */
export async function login(data) {
  return postJson('/usuario/login', data)
}

/**
 * Registra un nuevo usuario.
 * @param {{nombre_usuario: string, correo: string, contrasena: string, pais: string, idioma: string, disclosure: boolean}} data
 */
export async function register(data) {
  const formData = new FormData();
  formData.append('nombre_usuario', data.nombre_usuario);
  formData.append('correo', data.correo);
  formData.append('contrasena', data.contrasena);
  formData.append('pais', data.pais);
  formData.append('idioma', data.idioma);
  formData.append('disclosure', data.disclosure);             // Puede cambiar para ser un string que diga aceptado, o un int
  return postJson('/usuario/registro', formData, {}, true);
}

