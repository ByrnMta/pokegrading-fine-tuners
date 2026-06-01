import { useState } from 'react'
import Navbar from '../components/cards/Navbar'
import AddCardForm from '../components/cards/AddCardForm'
import { compareCard } from '../services/cards/api_cards'

/**
 * Vista para usuarios tipo Submitter.
 *
 * Flujo:
 *  1. El usuario llena el formulario (imagen obligatoria; metadatos opcionales).
 *  2. "Crear carta"   → AddCardForm lo maneja internamente vía onSuccess.
 *  3. "Comparar carta"→ AddCardForm construye el FormData y llama a onCompare(fd),
 *                       que aquí dispara compareCard y actualiza los resultados.
 */
export default function SubmitView() {
    const [results, setResults] = useState([])
    const [compareError, setCompareError] = useState(null)

    // Recibe el FormData ya construido y validado desde AddCardForm
    const handleCompare = async (formData) => {
    setCompareError(null)
    setResults([])

    try {
        const res = await compareCard(formData)

        const cards = Array.isArray(res)
            ? res
            : Array.isArray(res?.cards)
                ? res.cards
                : Array.isArray(res?.matches)
                    ? res.matches
                    : []

        setResults(cards.slice(0, 3))
    } catch (err) {
        const message = err?.data?.message || err?.message || 'Error al comparar la carta'
        setCompareError(message)
        throw err
    }
}

    const handleSuccess = (res) => {
        console.log('Carta creada:', res)
        setResults([])   // limpia resultados previos al crear una nueva carta
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            <Navbar />

            <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <section className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20">
                    <h1 className="mt-2 mb-6 text-2xl font-semibold text-white">
                        Vista Submitter
                        
                    </h1>

                    <AddCardForm
                        onSuccess={handleSuccess}
                        onCompare={handleCompare}
                        requiredFields={[]}
                        showMetadataFields={false} // oculta campos de metadatos para simplificar el formulario
                        submitLabel="Enviar a revisión"
                    />
                </section>

                {/* Resultados de comparación */}
                {results.length > 0 && (
                    <section className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20">
                        <h2 className="mb-4 text-lg font-semibold text-white">
                            Cartas similares encontradas ({results.length})
                        </h2>

                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                            {results.map((card, idx) => (
                                <div
                                    key={idx}
                                    className="rounded-xl border border-white/10 bg-white/5 p-3 transition hover:bg-white/10"
                                >
                                    {card.imagen_url && (
                                        <img
                                            src={card.imagen_url}
                                            alt={card.descripcion || `Carta ${idx + 1}`}
                                            className="w-full rounded-md object-cover"
                                            loading="lazy"
                                        />
                                    )}
                                    <div className="mt-3 space-y-1">
                                        {card.descripcion && (
                                            <p className="text-sm text-white">{card.descripcion}</p>
                                        )}
                                        {card.set_name && (
                                            <p className="text-xs text-gray-400">
                                                Set: <span className="text-gray-200">{card.set_name}</span>
                                            </p>
                                        )}
                                        {card.numero && (
                                            <p className="text-xs text-gray-400">
                                                Nº <span className="text-gray-200">{card.numero}</span>
                                            </p>
                                        )}
                                        {card.similitud !== undefined && (
                                            <p className="text-xs text-gray-400">
                                                Similitud:{' '}
                                                <span className="text-emerald-400 font-medium">
                                                    {Math.round(card.similitud * 100)}%
                                                </span>
                                            </p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {compareError && (
                    <p className="mt-4 text-sm text-rose-400">{compareError}</p>
                )}
            </main>
        </div>
    )
}