const API_URL_BASE = import.meta.env.VITE_API_BASE_URL;

/** 
 * Función para realizar solicitudes HTTP a la API.
 * Maneja la construcción de la solicitud, el procesamiento de la respuesta y el manejo de errores.
 * Devuelve la data de la respuesta del backend o lanza un error con `error.data`.
 * 
 * @param {string} path - Ruta de la API a la que se realizará la solicitud.
 * @param {Object} options - Opciones para configurar la solicitud (method, headers, body).
*/
async function request(path, options = {}) {
    
    // Configuración de la solicitud
    const method = options.method
    const headers = options.headers || {}
    const body = options.body

    if (!method) {
        throw new Error('Debes indicar method en request')
    }

    // Construye la URL completa y configura los headers
    const url = `${API_URL_BASE}${path}`
    const request_header = { ...headers, }

    // Si hay body, establecer Content-Type JSON
    const hasBody = body !== undefined && body !== null
    if (hasBody) {
        request_header['Content-Type'] = 'application/json'
    }

    // Preparar body para fetch: siempre JSON
    const fetchBody = hasBody ? JSON.stringify(body) : undefined

    // Realiza la solicitud usando fetch
    const response = await fetch(url, {
        method,
        headers: request_header,
        body: fetchBody,
    })

    // Parseo JSON si el Content-Type indica JSON, si no texto
    const contentType = response.headers.get('Content-Type') || ''
    const isJson = contentType.includes('application/json')
    const data = isJson ? await response.json() : await response.text()

    // Si la respuesta no es ok, lanzar un error con el mensaje adecuado
    if (!response.ok) {
        const message = (data && (data.detail || data.message)) || 
                        (typeof data === 'string' && data) || 
                        'Fallo en la solicitud'
        const error = new Error(message)
        error.status = response.status
        error.data = data
        throw error
    }

    return data
}

/**
 * Función helper para realizar solicitud HTTP GET
 * 
 * @param {string} path - Ruta de la API
 * @param {Object} options - Opciones para la solicitud (GET y {})
 */
export async function getJson(path, headers = {}) {
    return request(path, { method: 'GET', headers })
}

/** * Función helper para realizar solicitud HTTP POST
 * 
 * @param {string} path - Ruta de la API
 * @param {Object} options - Opciones para la solicitud (POST, {} y body)
 */
export async function postJson(path, body, headers = {}) {
    return request(path, { method: 'POST', headers, body })
}

/**
 * Función helper para realizar solicitud HTTP PUT
 * 
 * @param {string} path - Ruta de la API
 * @param {Object} options - Opciones para la solicitud (PUT, {} y body)
 */
export async function putJson(path, body, headers = {}) {
    return request(path, { method: 'PUT', headers, body })
}

/** 
 * Función helper para realizar solicitud HTTP DELETE
 * 
 * @param {string} path - Ruta de la API
 * @param {Object} options - Opciones para la solicitud (DELETE, {})
 */
export async function delJson(path, headers = {}) {
    return request(path, { method: 'DELETE', headers })
}
