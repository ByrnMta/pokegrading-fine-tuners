/**
 * Input reutilizable para cargar una imagen de carta en el flujo Submitter.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {string} props.label - Texto del label del input.
 * @param {File|null} props.file - Archivo actualmente seleccionado.
 * @param {string} [props.error] - Mensaje de error asociado al input.
 * @param {(event: React.ChangeEvent<HTMLInputElement>) => void} props.onChange - Callback al seleccionar archivo.
 * @param {() => void} props.onOpen - Callback para abrir la imagen seleccionada.
 * @param {string} [props.readyMessage] - Mensaje cuando hay archivo seleccionado.
 * @param {string} [props.emptyMessage] - Mensaje cuando no hay archivo seleccionado.
 * @returns {JSX.Element}
 */
export default function SubmitterImageInput({
    label,
    file = null,
    error = '',
    onChange = () => { },
    onOpen = () => { },
    readyMessage = 'Imagen lista para revisar.',
    emptyMessage = 'No se ha seleccionado ninguna imagen.',
}) {
    return (
        <div>
            <label className="flex flex-col">
                <span className="text-sm">
                    {label}
                </span>

                <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.heic,.heif,image/*"
                    onChange={onChange}
                    className="mt-2 block w-full cursor-pointer rounded-md border border-white/10 bg-white/5 px-4 py-3 text-sm text-white file:mr-4 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-1 file:text-white hover:bg-white/3"
                />

                {error && (
                    <small className="text-rose-400">
                        {error}
                    </small>
                )}
            </label>

            <div className="mt-2 flex flex-wrap items-center gap-2">
                <button
                    type="button"
                    disabled={!file}
                    onClick={onOpen}
                    className="rounded-md border border-white/10 px-2 py-1 text-xs text-gray-200 disabled:opacity-40"
                >
                    Abrir en el navegador
                </button>

                <span className="text-xs text-gray-400">
                    {file ? readyMessage : emptyMessage}
                </span>
            </div>
        </div>
    )
}