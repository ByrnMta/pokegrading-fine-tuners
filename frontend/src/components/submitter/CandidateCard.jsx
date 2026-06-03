/**
 * Tarjeta individual para mostrar una coincidencia de carta.
 *
 * No muestra imagen. Solo renderiza metadata y porcentaje de similitud.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {Object} props.candidate - Candidato recibido desde compare.
 * @param {boolean} props.selected - Indica si este candidato está seleccionado.
 * @param {(candidate: Object) => void} props.onSelect - Callback de selección.
 * @returns {JSX.Element}
 */
export default function CandidateCard({
    candidate,
    selected = false,
    onSelect = () => { },
}) {
    const score = Math.min(Number(candidate.score || 0) * 100, 100).toFixed(2)

    const cardClassName = selected
        ? 'rounded-xl border border-indigo-400 bg-indigo-500/20 p-4 text-left shadow-lg shadow-indigo-950/30'
        : 'rounded-xl border border-white/10 bg-white/5 p-4 text-left hover:bg-white/10'

    return (
        <button
            type="button"
            onClick={() => onSelect(candidate)}
            className={cardClassName}
        >
            <div className="flex items-start justify-between gap-3">
                <h3 className="font-semibold text-white">
                    {candidate.nombre || candidate.name || 'Carta sin nombre'}
                </h3>

                <span className="rounded-full bg-white/10 px-2 py-1 text-xs text-gray-200">
                    {score}%
                </span>
            </div>

            <dl className="mt-3 space-y-1 text-sm text-gray-300">
                <div>
                    <dt className="inline text-gray-400">Set: </dt>
                    <dd className="inline">{candidate.set_name || candidate.set || '-'}</dd>
                </div>

                <div>
                    <dt className="inline text-gray-400">Número: </dt>
                    <dd className="inline">{candidate.numero || candidate.number || '-'}</dd>
                </div>

                <div>
                    <dt className="inline text-gray-400">Edición: </dt>
                    <dd className="inline">{candidate.edicion || candidate.edition || '-'}</dd>
                </div>

                <div>
                    <dt className="inline text-gray-400">Idioma: </dt>
                    <dd className="inline">{candidate.idioma || candidate.language || '-'}</dd>
                </div>

                <div>
                    <dt className="inline text-gray-400">Acabado: </dt>
                    <dd className="inline">{candidate.acabado || candidate.finish || '-'}</dd>
                </div>
            </dl>
        </button>
    )
}