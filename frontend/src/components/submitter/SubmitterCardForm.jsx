import { useState } from 'react'
import CandidateList from './CandidateList'
// import MetadataEditor from './MetadataEditor'
import SubmitterImageInput from './SubmitterImageInput'
import useSubmitterCards from '../../hooks/submitter/useSubmitterCards'
import {
    //SUBMITTER_INITIAL_METADATA,
    SUBMITTER_IMAGE_LABEL,
    SUBMITTER_IMAGE_SIDE,
} from '../../constants/submitter'
import {
    handleSubmitterFile,
    handleOpenSubmitterImage,
    handleSubmitterCompare,
    handleSubmitterCandidateSelect,
    // handleSubmitterAutofill,
    // handleSubmitterMetadataChange,
    handleSubmitterSubmit,
} from '../../handlers/submitterHandlers'

/**
 * Formulario principal para el flujo Submitter.
 *
 * Coordina estados, eventos de UI y renderizado del flujo.
 * La logica pesada del flujo se delega a submitterHandlers.
 * La comunicacion con backend se obtiene desde useSubmitterCards.
 *
 * @returns {JSX.Element}
 */
export default function SubmitterCardForm() {
    const { compareCard, submitCard } = useSubmitterCards()

    const [frontFile, setFrontFile] = useState(null)
    const [backFile, setBackFile] = useState(null)
    const [errors, setErrors] = useState({})
    const [compareLoading, setCompareLoading] = useState(false)
    const [submitLoading, setSubmitLoading] = useState(false)

    const [candidates, setCandidates] = useState([])
    const [selectedCandidate, setSelectedCandidate] = useState(null)

    // Se mantiene por compatibilidad con handlers y posible reactivacion futura.
    // Por ahora no se muestra formulario editable de metadata.
    //const [metadata, setMetadata] = useState(SUBMITTER_INITIAL_METADATA)

    const onFileChange = (event, side) => {
        handleSubmitterFile({
            event,
            side,
            setFrontFile,
            setBackFile,
            setErrors,
        })
    }

    const onOpenImage = (side) => {
        handleOpenSubmitterImage({
            side,
            frontFile,
            backFile,
        })
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
        handleSubmitterCandidateSelect({
            candidate,
            setSelectedCandidate,
            setErrors,
        })
    }

    /*
    const onAutofill = () => {
        handleSubmitterAutofill({
            selectedCandidate,
            setMetadata,
            setErrors,
        })
    }

    const onMetadataChange = (event) => {
        handleSubmitterMetadataChange({
            event,
            setMetadata,
            setErrors,
        })
    }
    */

    const onSubmit = (event) => {
    handleSubmitterSubmit({
        event,
        frontFile,
        backFile,
        submitCard,
        setErrors,
        setSubmitLoading,
    })
}

    return (
        <form onSubmit={onSubmit} className="space-y-6">
            <section className="space-y-4">
                <h2 className="text-lg font-semibold text-white">
                    Imágenes de la carta
                </h2>

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

                <div className="grid gap-3 sm:grid-cols-2">
                    <button
                        type="button"
                        disabled={compareLoading}
                        onClick={onCompare}
                        className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
                    >
                        {compareLoading ? 'Comparando...' : 'Búsqueda rápida'}
                    </button>

                    <button
                        type="submit"
                        disabled={submitLoading}
                        className="flex w-full justify-center rounded-md bg-emerald-600 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-emerald-500 disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500"
                    >
                        {submitLoading ? 'Enviando...' : 'Enviar carta'}
                    </button>
                </div>

                {errors.compare && (
                    <p className="text-sm text-rose-400">
                        {errors.compare}
                    </p>
                )}

                {errors.submit && (
                    <p className="text-sm text-rose-400">
                        {errors.submit}
                    </p>
                )}

                {errors.success && (
                    <p className="text-sm text-emerald-400">
                        {errors.success}
                    </p>
                )}
            </section>

            <CandidateList
                candidates={candidates}
                selectedCandidate={selectedCandidate}
                onSelect={onSelectCandidate}
            />

            {/*
            {candidates.length > 0 && (
                <MetadataEditor
                    metadata={metadata}
                    selectedCandidate={selectedCandidate}
                    errors={errors}
                    onChange={onMetadataChange}
                    onAutofill={onAutofill}
                />
            )}
            */}
        </form>
    )
}