import { postFormData } from '../api_client'

// ─────────────────────────────────────────────
//  Mock — activar con VITE_MOCK_COMPARE=true en .env.local
//  Simula el delay de red y devuelve 3 cartas de ejemplo.
// ─────────────────────────────────────────────
const USE_MOCK = import.meta.env.VITE_MOCK_COMPARE === 'true'

const MOCK_CARDS = [
    {
        imagen_url: 'https://images.pokemontcg.io/base1/4_hires.png',
        descripcion: 'Charizard Base Set',
        set_name: 'Base Set',
        numero: '4/102',
        similitud: 0.97,
    },
    {
        imagen_url: 'https://images.pokemontcg.io/base1/4_hires.png',
        descripcion: 'Charizard Base Set 2',
        set_name: 'Base Set 2',
        numero: '4/130',
        similitud: 0.84,
    },
    {
        imagen_url: 'https://images.pokemontcg.io/base1/4_hires.png',
        descripcion: 'Charizard Legendary Collection',
        set_name: 'Legendary Collection',
        numero: '3/110',
        similitud: 0.76,
    },
]

async function mockCompareCard() {
    // Simula latencia de red (800 ms)
    await new Promise((resolve) => setTimeout(resolve, 800))
    return { cards: MOCK_CARDS }
}
// ─────────────────────────────────────────────
// FIN MOCK
// ─────────────────────────────────────────────

export async function postCard(formData) {
    return postFormData('/catalogo/carta', formData)
}
/**
 * Compara una carta enviada con las existentes en la base de datos.
 * Devuelve hasta 3 coincidencias potenciales.
 */
export async function compareCard(formData) {
    if (USE_MOCK) return mockCompareCard() //mock
    return postFormData('/catalogo/carta/compare', formData)
}