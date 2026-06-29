import SubgradeBar from './SubgradeBar'
import { SUBGRADE_LABELS, SUBGRADE_ORDER } from '../../constants/grading'

const BASELINE_LABEL = {
    SET_ACABADO: 'Set + Acabado · Calibrado',
    GLOBAL: 'Global (fallback)',
}

const COHERENCE_BADGE = {
    REVIEW: {
        label: 'Revisión humana pendiente',
        class: 'bg-amber-500/15 text-amber-300 border border-amber-500/30',
    },
    OK: null,
}

/**
 * Panel que muestra el resultado de la calificación de una carta.
 *
 * Maneja tres casos según el estado del backend:
 * - AUTO: calificación completa, muestra subgrades y grado final.
 * - REVIEW: calificación con incoherencia interna, muestra datos + badge de advertencia.
 * - MANUAL: sin calificación automática, muestra solo el mensaje del backend.
 *
 * Solo muestra `mensaje` y `calificacion`, según lo indicado en el .md.
 *
 * @param {Object} props
 * @param {Object} props.result - Resultado normalizado por normalizeGradingResult.
 * @param {Function} props.onReset - Callback para reiniciar el flujo.
 * @returns {JSX.Element}
 */
export default function GradingResult({ result, onReset }) {
    const mensaje        = result?.mensaje        || null
    const estado         = result?.estado         || null
    const calificacion   = result?.subgrades      || null
    const gradoFinal     = Number(result?.grado_final   ?? 0)
    const incertidumbre  = Number(result?.incertidumbre ?? 0)
    const coherenceFlag  = result?.coherence_flag || null
    const baselineOrigen = result?.baseline_origen || null
    const version        = result?.version_algoritmo || null
    const idEvaluacion   = result?.id_evaluacion  || null

    const isManual = estado === 'MANUAL'
    const hasGrade = !isManual && calificacion

    const gradoMin = Math.max(0, gradoFinal - incertidumbre).toFixed(1)
    const gradoMax = Math.min(10, gradoFinal + incertidumbre).toFixed(1)

    const gradoColor =
        gradoFinal >= 8 ? 'text-emerald-400'
        : gradoFinal >= 6 ? 'text-indigo-300'
        : gradoFinal >= 4 ? 'text-amber-400'
        : 'text-rose-400'

    const coherenceBadge = coherenceFlag ? COHERENCE_BADGE[coherenceFlag] : null

    return (
        <div className="space-y-6">

            {/* Mensaje del backend */}
            {mensaje && (
                <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-gray-300">
                    {mensaje}
                </div>
            )}

            {/* Badge de revisión humana */}
            {coherenceBadge && (
                <div className={`rounded-lg px-4 py-2 text-sm font-medium ${coherenceBadge.class}`}>
                    {coherenceBadge.label}
                </div>
            )}

            {/* Estado MANUAL: sin calificación automática */}
            {isManual && (
                <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-5 text-center">
                    <p className="mt-3 text-sm text-amber-300 font-semibold">
                        Derivada a calificación manual
                    </p>
                    <p className="mt-1 text-xs text-gray-400">
                        Te notificaremos cuando el resultado esté disponible.
                    </p>
                </div>
            )}

            {/* Grado final */}
            {hasGrade && (
                <>
                    <div className="flex flex-col items-center gap-1 py-4">
                        <span className="text-sm text-gray-400">Grado estimado</span>

                        <span className={`text-6xl font-bold tabular-nums ${gradoColor}`}>
                            {gradoFinal.toFixed(1)}
                        </span>

                        {incertidumbre > 0 && (
                            <span className="text-sm text-gray-400">
                                Rango: {gradoMin} – {gradoMax}
                            </span>
                        )}
                    </div>

                    {/* Subgrades */}
                    <section className="space-y-3">
                        <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-400">
                            Subgrades por dimensión
                        </h3>

                        <div className="space-y-3">
                            {SUBGRADE_ORDER.map((key) => (
                                <SubgradeBar
                                    key={key}
                                    label={SUBGRADE_LABELS[key] ?? key}
                                    value={calificacion[key] ?? 0}
                                />
                            ))}
                        </div>
                    </section>

                    {/* Detalles */}
                    <section className="space-y-2 rounded-xl border border-white/10 bg-white/5 p-4 text-sm">
                        <h3 className="font-semibold text-gray-300">Detalles de la evaluación</h3>

                        <dl className="space-y-1.5 text-gray-400">
                            {baselineOrigen && (
                                <div className="flex justify-between gap-4">
                                    <dt>Baseline</dt>
                                    <dd className="text-right text-gray-200">
                                        {BASELINE_LABEL[baselineOrigen] ?? baselineOrigen}
                                    </dd>
                                </div>
                            )}

                            {version && (
                                <div className="flex justify-between gap-4">
                                    <dt>Versión del algoritmo</dt>
                                    <dd className="font-mono text-xs text-gray-200">{version}</dd>
                                </div>
                            )}

                            {idEvaluacion && (
                                <div className="flex justify-between gap-4">
                                    <dt>ID evaluación</dt>
                                    <dd className="font-mono text-xs text-gray-200 break-all">
                                        {idEvaluacion}
                                    </dd>
                                </div>
                            )}
                        </dl>
                    </section>
                </>
            )}

            <button
                type="button"
                onClick={onReset}
                className="w-full rounded-md border border-white/10 px-3 py-2 text-sm text-gray-300 hover:bg-white/5"
            >
                Evaluar otra carta
            </button>
        </div>
    )
}
