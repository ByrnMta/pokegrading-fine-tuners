const TYPE_CONFIG = {
    manual_review: {
        title: 'Derivada a revisión manual',
        defaultMessage:
            'La carta fue derivada para revisión por un calificador humano. El resultado estará disponible próximamente.',
        actionLabel: 'Enviar otra carta',
        borderClass: 'border-amber-500/30 bg-amber-500/5',
        textClass: 'text-amber-300',
    },
    recapture: {
        title: 'Se requiere recapturar la imagen',
        defaultMessage:
            'La imagen tiene distorsiones que no pueden corregirse automáticamente. Por favor, recaptura la carta con mejor iluminación y encuadre.',
        actionLabel: 'Intentar de nuevo',
        borderClass: 'border-indigo-500/30 bg-indigo-500/5',
        textClass: 'text-indigo-300',
    },
}

const FALLBACK_CONFIG = {
    title: 'Ocurrió un error',
    defaultMessage: 'No se pudo completar la evaluación. Por favor, intenta de nuevo.',
    actionLabel: 'Intentar de nuevo',
    borderClass: 'border-rose-500/30 bg-rose-500/5',
    textClass: 'text-rose-300',
}

/**
 * Pantalla de estado para flujos alternos del grading:
 * revisión manual o recaptura requerida.
 *
 * @param {Object} props
 * @param {'manual_review'|'recapture'} props.type - Tipo de derivación.
 * @param {string|null} props.message - Mensaje específico del backend.
 * @param {Function} props.onReset - Callback para reiniciar el flujo.
 * @returns {JSX.Element}
 */
export default function GradingAlternate({ type, message, onReset }) {
    const config = TYPE_CONFIG[type] || FALLBACK_CONFIG

    return (
        <div className="space-y-5">
            <div className={`rounded-xl border p-5 text-center ${config.borderClass}`}>
                <h3 className={`text-base font-semibold ${config.textClass}`}>
                    {config.title}
                </h3>

                <p className="mt-2 text-sm text-gray-400">
                    {message || config.defaultMessage}
                </p>
            </div>

            <button
                type="button"
                onClick={onReset}
                className="w-full rounded-md border border-white/10 px-3 py-2 text-sm text-gray-300 hover:bg-white/5"
            >
                {config.actionLabel}
            </button>
        </div>
    )
}
