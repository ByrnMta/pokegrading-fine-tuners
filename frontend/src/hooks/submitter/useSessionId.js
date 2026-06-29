import { useState } from 'react'

/**
 * Genera un identificador de sesión único al montar el componente.
 *
 * Simula el token de inicio de sesión del submitter: se crea una sola vez
 * por visita y se mantiene estable durante toda la sesión activa.
 * Se adjunta al FormData de envío como `id_sesion`.
 *
 * Formato: submitter-<timestamp>-<random hex>
 *
 * @returns {{ sessionId: string }}
 */
export default function useSessionId() {
    const [sessionId] = useState(() => {
        const ts = Date.now().toString(36)
        const rand = Math.random().toString(36).slice(2, 8)
        return `submitter-${ts}-${rand}`
    })
    console.log('Generated sessionId:', sessionId) // Debug log
    return { sessionId }
}
