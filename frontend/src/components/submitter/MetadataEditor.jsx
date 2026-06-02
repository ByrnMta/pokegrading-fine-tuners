const metadataFields = [
    {
        name: 'nombre',
        label: 'Nombre',
        type: 'text',
    },
    {
        name: 'set_name',
        label: 'Set',
        type: 'text',
    },
    {
        name: 'numero',
        label: 'Número',
        type: 'text',
    },
    {
        name: 'edicion',
        label: 'Edición',
        type: 'text',
    },
    {
        name: 'idioma',
        label: 'Idioma',
        type: 'text',
    },
    {
        name: 'acabado',
        label: 'Acabado',
        type: 'text',
    },
    {
        name: 'rareza',
        label: 'Rareza',
        type: 'text',
    },
    {
        name: 'tipo',
        label: 'Tipo',
        type: 'text',
    },
    {
        name: 'hp',
        label: 'HP',
        type: 'text',
        inputMode: 'numeric',
    },
    {
        name: 'ilustrador',
        label: 'Ilustrador',
        type: 'text',
    },
    {
        name: 'anio_impresion',
        label: 'Año de impresión',
        type: 'text',
        inputMode: 'numeric',
    },
]

/**
 * Editor de metadata para la carta enviada por Submitter.
 *
 * Permite autorellenar datos desde el candidato seleccionado o editar
 * manualmente cada campo antes del envío final.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {Object} props.metadata - Metadata editable actual.
 * @param {Object|null} props.selectedCandidate - Candidato seleccionado.
 * @param {Object} props.errors - Errores actuales del formulario.
 * @param {(event: React.ChangeEvent<HTMLInputElement>) => void} props.onChange - Callback de edición.
 * @param {() => void} props.onAutofill - Callback para autorellenar metadata.
 * @returns {JSX.Element|null}
 */
export default function MetadataEditor({
    metadata = {},
    selectedCandidate = null,
    errors = {},
    onChange = () => { },
    onAutofill = () => { },
}) {
    return (
        <section className="space-y-4 border-t border-white/10 pt-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-lg font-semibold text-white">
                        Metadata de la carta
                    </h2>

                    <p className="text-sm text-gray-400">
                        Puedes autorellenar con el candidato seleccionado o completar los datos manualmente.
                    </p>
                </div>

                <button
                    type="button"
                    disabled={!selectedCandidate}
                    onClick={onAutofill}
                    className="rounded-md border border-white/10 px-3 py-2 text-sm font-medium text-gray-200 hover:bg-white/5 disabled:opacity-40"
                >
                    Autorellenar
                </button>
            </div>

            {errors.metadata && (
                <p className="text-sm text-rose-400">
                    {errors.metadata}
                </p>
            )}

            <div className="grid gap-4 md:grid-cols-2">
                {metadataFields.map((field) => (
                    <label key={field.name} className="flex flex-col">
                        <span className="text-sm">
                            {field.label}
                        </span>

                        <input
                            name={field.name}
                            type={field.type}
                            value={metadata[field.name] || ''}
                            onChange={onChange}
                            inputMode={field.inputMode}
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        />

                        {errors[field.name] && (
                            <small className="text-rose-400">
                                {errors[field.name]}
                            </small>
                        )}
                    </label>
                ))}
            </div>
        </section>
    )
}