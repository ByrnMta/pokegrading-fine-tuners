/**
 * Barra visual para un subgrade individual.
 *
 * Muestra el nombre de la dimensión, el valor numérico y una barra
 * de progreso proporcional a la escala 1.0–10.0.
 *
 * @param {Object} props
 * @param {string} props.label - Nombre de la dimensión (ej. "Centering").
 * @param {number} props.value - Valor del subgrade (1.0–10.0).
 * @returns {JSX.Element}
 */
export default function SubgradeBar({ label, value }) {
    const clamped = Math.min(Math.max(Number(value) || 0, 0), 10)
    const percent = (clamped / 10) * 100

    const barColor =
        clamped >= 8
            ? 'bg-emerald-500'
            : clamped >= 6
            ? 'bg-indigo-400'
            : clamped >= 4
            ? 'bg-amber-400'
            : 'bg-rose-500'

    return (
        <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
                <span className="text-gray-300">{label}</span>
                <span className="font-semibold tabular-nums text-white">
                    {clamped.toFixed(1)}
                </span>
            </div>

            <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                <div
                    className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                    style={{ width: `${percent}%` }}
                />
            </div>
        </div>
    )
}
