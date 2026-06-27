import SubgradeBar from './SubgradeBar'
import { SUBGRADE_LABELS, SUBGRADE_ORDER } from '../../constants/grading'

/**
 * Panel que muestra el resultado completo de la calificación de una carta.
 *
 * Incluye: grado final, banda de incertidumbre, subgrades por dimensión,
 * baseline utilizado y versión del algoritmo.
 *
 * @param {Object} props
 * @param {Object} props.result - Resultado devuelto por el backend de calificación.
 * @param {Function} props.onReset - Callback para reiniciar el flujo.
 * @returns {JSX.Element}
 */
export default function GradingResult({ result, onReset }) {
    const gradoFinal = Number(result?.grado_final ?? 0)
    const incertidumbre = Number(result?.incertidumbre ?? 0)
    const subgrades = result?.subgrades || {}
    const baseline = result?.baseline_usado || {}
    const versionAlgoritmo = result?.version_algoritmo || 'desconocida'
    const idEvaluacion = result?.id_evaluacion || '-'

    const gradoMin = Math.max(0, gradoFinal - incertidumbre).toFixed(1)
    const gradoMax = Math.min(10, gradoFinal + incertidumbre).toFixed(1)

    const gradoColor =
        gradoFinal >= 8
            ? 'text-emerald-400'
            : gradoFinal >= 6
            ? 'text-indigo-300'
            : gradoFinal >= 4
            ? 'text-amber-400'
            : 'text-rose-400'

    const baselineLabel =
        baseline?.tipo === 'calibrado'
            ? `${baseline.set_name || ''} / ${baseline.acabado || ''} · Calibrado`
            : 'Global (fallback)'

    return (
        <div className="space-y-6">
            <div className="flex flex-col items-center gap-1 py-4">
                <span className="text-sm text-gray-400">Grado estimado</span>

                <span className={`text-6xl font-bold tabular-nums ${gradoColor}`}>
                    {gradoFinal.toFixed(1)}
                </span>

                {incertidumbre > 0 && (
                    <span className="text-sm text-gray-400">
                        Rango estimado: {gradoMin} – {gradoMax}
                    </span>
                )}
            </div>

            <section className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-400">
                    Subgrades por dimensión
                </h3>

                <div className="space-y-3">
                    {SUBGRADE_ORDER.map((key) => (
                        <SubgradeBar
                            key={key}
                            label={SUBGRADE_LABELS[key] ?? key}
                            value={subgrades[key] ?? 0}
                        />
                    ))}
                </div>
            </section>

            <section className="space-y-2 rounded-xl border border-white/10 bg-white/5 p-4 text-sm">
                <h3 className="font-semibold text-gray-300">Detalles de la evaluación</h3>

                <dl className="space-y-1.5 text-gray-400">
                    <div className="flex justify-between gap-4">
                        <dt>Baseline</dt>
                        <dd className="text-right text-gray-200">{baselineLabel}</dd>
                    </div>

                    <div className="flex justify-between gap-4">
                        <dt>Versión del algoritmo</dt>
                        <dd className="font-mono text-xs text-gray-200">{versionAlgoritmo}</dd>
                    </div>

                    <div className="flex justify-between gap-4">
                        <dt>ID evaluación</dt>
                        <dd className="font-mono text-xs text-gray-200 break-all">{idEvaluacion}</dd>
                    </div>
                </dl>
            </section>

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
