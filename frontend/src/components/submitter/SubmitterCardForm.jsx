import { useState } from 'react'
import CandidateList from './CandidateList'
import SubmitterImageInput from './SubmitterImageInput'
import GradingResult from '../grading/GradingResult'
import GradingAlternate from '../grading/GradingAlternate'
import useSubmitterCards from '../../hooks/submitter/useSubmitterCards'
import useSessionId from '../../hooks/submitter/useSessionId'
import {
    SUBMITTER_IMAGE_LABEL,
    SUBMITTER_IMAGE_SIDE,
    CARD_SET_OPTIONS,
} from '../../constants/submitter'
import {
    handleSubmitterFile,
    handleOpenSubmitterImage,
    handleSubmitterCompare,
    handleSubmitterCandidateSelect,
    handleSubmitterSubmit,
} from '../../handlers/submitterHandlers'

/**
 * Formulario principal para el flujo Submitter.
 *
 * Flujo:
 * 1. Al montar, se genera un id_sesion único (token de sesión).
 * 2. El usuario sube imágenes frontal y reverso.
 * 3. Opcionalmente realiza una búsqueda rápida de candidatos.
 * 4. Selecciona el set y acabado de la carta.
 * 5. Envía la carta: el backend corre el pipeline completo y devuelve
 *    el resultado (AUTO, REVIEW, MANUAL o IDEMPOTENCIA).
 * 6. Se muestra GradingResult con mensaje y calificación.
 *
 * @returns {JSX.Element}
 */
export default function SubmitterCardForm() {
    const { compareCard, submitCard } = useSubmitterCards()
    const { sessionId } = useSessionId()

    const [frontFile, setFrontFile] = useState(null)
    const [backFile, setBackFile] = useState(null)
    const [errors, setErrors] = useState({})
    const [compareLoading, setCompareLoading] = useState(false)
    const [submitLoading, setSubmitLoading] = useState(false)

    const [candidates, setCandidates] = useState([])
    const [selectedCandidate, setSelectedCandidate] = useState(null)

    // Select de set + acabado: almacena el índice de CARD_SET_OPTIONS
    const [selectedSetIndex, setSelectedSetIndex] = useState('')

    // Resultado del pipeline de grading
    const [gradingResult, setGradingResult] = useState(null)
    const [gradingDerivation, setGradingDerivation] = useState(null)

    const selectedOption = selectedSetIndex !== '' ? CARD_SET_OPTIONS[selectedSetIndex] : null

    const onFileChange = (event, side) => {
        handleSubmitterFile({ event, side, setFrontFile, setBackFile, setErrors })
    }

    const onOpenImage = (side) => {
        handleOpenSubmitterImage({ side, frontFile, backFile })
    }

    const onCompare = () => {
        handleSubmitterCompare({
            frontFile,
            backFile,
            compareCard,
            setErrors,
            setSelectedCandidate,
            setCandidates,
            setCompareLoading,
        })
    }

    const onSelectCandidate = (candidate) => {
        handleSubmitterCandidateSelect({ candidate, setSelectedCandidate, setErrors })
    }

    const onSubmit = (event) => {
        if (!selectedOption) {
            event.preventDefault()
            setErrors((prev) => ({ ...prev, set_name: 'Selecciona el set y acabado de la carta.' }))
            return
        }

        handleSubmitterSubmit({
            event,
            frontFile,
            backFile,
            sessionId,
            setName: selectedOption.set_name,
            acabado: selectedOption.acabado,
            submitCard,
            setErrors,
            setSubmitLoading,
            setGradingResult,
            setGradingDerivation,
        })
    }

    const onReset = () => {
        setFrontFile(null)
        setBackFile(null)
        setErrors({})
        setCandidates([])
        setSelectedCandidate(null)
        setSelectedSetIndex('')
        setGradingResult(null)
        setGradingDerivation(null)
    }

    // Resultado exitoso (AUTO, REVIEW, MANUAL, IDEMPOTENCIA)
    if (gradingResult) {
        return <GradingResult result={gradingResult} onReset={onReset} />
    }

    // Derivación a revisión manual o recaptura (errores estructurales)
    if (gradingDerivation) {
        return (
            <GradingAlternate
                type={gradingDerivation.type}
                message={gradingDerivation.message}
                onReset={onReset}
            />
        )
    }

    return (
        <form onSubmit={onSubmit} className="space-y-6">
            <section className="space-y-4">
                <h2 className="text-lg font-semibold text-white">Imágenes de la carta</h2>

                <SubmitterImageInput
                    label={SUBMITTER_IMAGE_LABEL.FRONT}
                    file={frontFile}
                    error={errors.imagen_frontal}
                    onChange={(event) => onFileChange(event, SUBMITTER_IMAGE_SIDE.FRONT)}
                    onOpen={() => onOpenImage(SUBMITTER_IMAGE_SIDE.FRONT)}
                    readyMessage="Imagen frontal lista para revisar."
                    emptyMessage="No se ha seleccionado imagen frontal."
                />

                <SubmitterImageInput
                    label={SUBMITTER_IMAGE_LABEL.BACK}
                    file={backFile}
                    error={errors.imagen_reverso}
                    onChange={(event) => onFileChange(event, SUBMITTER_IMAGE_SIDE.BACK)}
                    onOpen={() => onOpenImage(SUBMITTER_IMAGE_SIDE.BACK)}
                    readyMessage="Imagen del reverso lista para revisar."
                    emptyMessage="No se ha seleccionado imagen del reverso."
                />
            </section>

            {/* Select de set + acabado */}
            <section className="space-y-2">
                <label
                    htmlFor="card-set-select"
                    className="block text-sm font-medium text-gray-300"
                >
                    Set y acabado *
                </label>

                <select
                    id="card-set-select"
                    value={selectedSetIndex}
                    onChange={(e) => {
                        setSelectedSetIndex(e.target.value)
                        setErrors((prev) => ({ ...prev, set_name: undefined }))
                    }}
                    className="w-full rounded-md border border-white/10 bg-gray-900 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
                    disabled={submitLoading}
                >
                    <option value="" disabled>Selecciona set y acabado...</option>
                    {CARD_SET_OPTIONS.map((opt, i) => (
                        <option key={i} value={i}>
                            {opt.set_name} · {opt.acabado}
                        </option>
                    ))}
                </select>

                {errors.set_name && (
                    <p className="text-sm text-rose-400">{errors.set_name}</p>
                )}
            </section>

            {/* Botones de acción */}
            <div className="grid gap-3 sm:grid-cols-2">
                <button
                    type="button"
                    disabled={compareLoading || submitLoading}
                    onClick={onCompare}
                    className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
                >
                    {compareLoading ? 'Comparando...' : 'Búsqueda rápida'}
                </button>

                <button
                    type="submit"
                    disabled={submitLoading || compareLoading}
                    className="flex w-full justify-center rounded-md bg-emerald-600 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-emerald-500 disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500"
                >
                    {submitLoading ? 'Procesando...' : 'Enviar carta'}
                </button>
            </div>

            {errors.compare && (
                <p className="text-sm text-rose-400">{errors.compare}</p>
            )}

            {errors.submit && (
                <p className="text-sm text-rose-400">{errors.submit}</p>
            )}

            <CandidateList
                candidates={candidates}
                selectedCandidate={selectedCandidate}
                onSelect={onSelectCandidate}
            />
        </form>
    )
}
