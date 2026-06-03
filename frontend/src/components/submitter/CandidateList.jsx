import CandidateCard from './CandidateCard'

/**
 * Lista de candidatos encontrados en la comparación.
 *
 * Renderiza hasta 3 coincidencias y delega la visualización individual
 * a CandidateCard.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {Array<Object>} props.candidates - Lista de candidatos recibidos.
 * @param {Object|null} props.selectedCandidate - Candidato actualmente seleccionado.
 * @param {(candidate: Object) => void} props.onSelect - Callback al seleccionar candidato.
 * @returns {JSX.Element|null}
 */
export default function CandidateList({
    candidates = [],
    selectedCandidate = null,
    onSelect = () => { },
}) {
    if (!candidates.length) {
        return null
    }

    const visibleCandidates = candidates.slice(0, 3)

    return (
        <section className="space-y-4 border-t border-white/10 pt-6">
            <div>
                <h2 className="text-lg font-semibold text-white">
                    Coincidencias encontradas
                </h2>

                <p className="mt-1 text-sm text-gray-400">
                    Selecciona una coincidencia.
                </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
                {visibleCandidates.map((candidate, index) => {
                    const candidateId =
                        candidate.card_id ||
                        candidate.id ||
                        `${candidate.nombre || candidate.name || 'candidate'}-${index}`

                    const selectedId =
                        selectedCandidate?.card_id ||
                        selectedCandidate?.id ||
                        null

                    const isSelected = selectedId === candidateId

                    return (
                        <CandidateCard
                            key={candidateId}
                            candidate={candidate}
                            selected={isSelected}
                            onSelect={onSelect}
                        />
                    )
                })}
            </div>
        </section>
    )
}