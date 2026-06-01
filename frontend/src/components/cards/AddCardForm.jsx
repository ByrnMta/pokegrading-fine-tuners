import { useState } from 'react'
import { postCard } from '../../services/cards/api_cards'

//const ALLOWED_EXT = ['jpeg', 'png', 'heic']
const ALLOWED_EXT = ['jpg', 'jpeg', 'png', 'heic', 'heif']

// Función auxiliar para obtener la extensión del archivo
function getExt(name) {
    return String(name).split('.').pop().toLowerCase()
}

export default function AddCardForm({
    onSuccess = () => {},
    onCompare = null,
    requiredFields = ['set_name', 'numero', 'edicion', 'idioma', 'acabado'],
    showMetadataFields = true,
    submitLabel = 'Crear carta',
}) {
    const [form, setForm] = useState({ set_name: '', numero: '', edicion: '', idioma: '', acabado: '' })
    const [file, setFile] = useState(null)
    const [errors, setErrors] = useState({})
    const [submitting, setSubmitting] = useState(false)
    const [comparing, setComparing] = useState(false)

    const isRequired = (field) => requiredFields.includes(field)

    // Construye FormData con los valores actuales
    const buildFormData = () => {
        const fd = new FormData()
        fd.append('numero', form.numero)
        fd.append('set_name', form.set_name)
        fd.append('edicion', form.edicion)
        fd.append('idioma', form.idioma)
        fd.append('acabado', form.acabado)
        if (file) fd.append('imagen', file)
        return fd
    }

    // Validación de campos antes de enviar
    const validateFields = (mode = 'submit') => {
        const err = {}

        if (isRequired('set_name') && !form.set_name) err.set_name = 'Requerido'
        if (isRequired('numero') && !form.numero) err.numero = 'Requerido'
        if (isRequired('edicion') && !form.edicion) err.edicion = 'Requerido'
        if (isRequired('idioma') && !form.idioma) err.idioma = 'Requerido'
        if (isRequired('acabado') && !form.acabado) err.acabado = 'Requerido'

        // La imagen siempre es obligatoria
        if (!file) err.imagen = 'Debe adjuntar una imagen de referencia'

        if (file) {
            const ext = getExt(file.name)
            if (!ALLOWED_EXT.includes(ext)) {
                err.imagen = 'Formato no soportado. Use jpg, jpeg, png, heic o heif.'
            }
        }

        return err
    }

    // Maneja la selección del archivo, valida formato, tamaño y resolución, y actualiza el estado de errores o del archivo
    const handleFile = async (ev) => {
        const f = ev.target.files?.[0] || null
        setFile(null)
        setErrors((e) => ({ ...e, imagen: undefined }))
        if (!f) return
        
        // Valida la extension del archivo (formato)
        const ext = getExt(f.name)
        if (!ALLOWED_EXT.includes(ext)) {
            setErrors((e) => ({ ...e, imagen: 'Formato no soportado. Use jpeg, png o heic.' }))
            return
        }
        setFile(f)
    }

    // Actualiza el estado de los inputs limpiando errores en cada campo
    const handleChange = (e) => {
        const { name, value } = e.target
        setForm((s) => ({ ...s, [name]: value }))
        setErrors((s) => ({ ...s, [name]: undefined }))
    }

    // Maneja el envío del formulario 
    const handleSubmit = async (e) => {
        e.preventDefault()
        setErrors({})
        const fieldErr = validateFields('submit')

        // Si hay errores de validación, no enviar y mostrar errores
        if (Object.keys(fieldErr).length) {
            setErrors(fieldErr)
            return
        }

        // Actualiza el estado a enviando
        setSubmitting(true)

        // Intenta enviar los datos al backend, maneja la respuesta exitosa o muestra errores de envío
        try {
            const res = await postCard(buildFormData())
            onSuccess(res)
            // Reset — corrección del typo 'numer' → 'numero'
            setForm({ set_name: '', numero: '', edicion: '', idioma: '', acabado: '' })
            setFile(null)
        } catch (err) {
            const message = err?.data?.message || err?.message || 'Error al crear la carta'
            setErrors({ submit: message })
        } finally {
            setSubmitting(false)
        }
    }

    // Acción exclusiva del modo Submitter: construye el FormData y se lo pasa al padre
    const handleCompare = async (e) => {
        e.preventDefault()
        setErrors({})

        // Para comparar solo necesitamos la imagen
        if (!file) {
            setErrors({ imagen: 'Debe adjuntar una imagen para comparar' })
            return
        }
        const ext = getExt(file.name)
        if (!ALLOWED_EXT.includes(ext)) {
            setErrors({ imagen: 'Formato no soportado. Use jpeg, png o heic.' })
            return
        }

        setComparing(true)
        try {
            await onCompare(buildFormData())
        } catch (err) {
            const message = err?.data?.message || err?.message || 'Error al comparar la carta'
            setErrors({ submit: message })
        } finally {
            setComparing(false)
        }
    }

    // Función para abrir la imagen seleccionada en una nueva pestaña del navegador
    const handleOpenInNewWindow = () => {
        if (!file) return
        const url = URL.createObjectURL(file)
        window.open(url, '_blank', 'noopener,noreferrer')
        setTimeout(() => URL.revokeObjectURL(url), 0)
    }

    return (
        <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-4">
            <div className="space-y-4">
                {showMetadataFields && (
                    <div className="space-y-3">
                        {/* Set */}
                        <label className="flex flex-col">
                            <span className="text-sm">
                                Set {isRequired('set_name') && '*'}
                            </span>
                            <input
                                name="set_name"
                                value={form.set_name}
                                onChange={handleChange}
                                className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                            />
                            {errors.set_name && <small className="text-rose-400">{errors.set_name}</small>}
                        </label>

                        {/* Número */}
                        <label className="flex flex-col">
                            <span className="text-sm">
                                Número {isRequired('numero') && '*'}
                            </span>
                            <input
                                name="numero"
                                value={form.numero}
                                onChange={handleChange}
                                className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                            />
                            {errors.numero && <small className="text-rose-400">{errors.numero}</small>}
                        </label>

                        {/* Edición */}
                        <label className="flex flex-col">
                            <span className="text-sm">
                                Edición {isRequired('edicion') && '*'}
                            </span>
                            <input
                                name="edicion"
                                value={form.edicion}
                                onChange={handleChange}
                                className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                            />
                            {errors.edicion && <small className="text-rose-400">{errors.edicion}</small>}
                        </label>

                        {/* Idioma */}
                        <label className="flex flex-col">
                            <span className="text-sm">
                                Idioma {isRequired('idioma') && '*'}
                            </span>
                            <input
                                name="idioma"
                                value={form.idioma}
                                onChange={handleChange}
                                className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                            />
                            {errors.idioma && <small className="text-rose-400">{errors.idioma}</small>}
                        </label>

                        {/* Acabado */}
                        <label className="flex flex-col">
                            <span className="text-sm">
                                Acabado {isRequired('acabado') && '*'}
                            </span>
                            <input
                                name="acabado"
                                value={form.acabado}
                                onChange={handleChange}
                                className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                            />
                            {errors.acabado && <small className="text-rose-400">{errors.acabado}</small>}
                        </label>
                    </div>
                )}

                {/* Imagen */}
                <div>
                    <label className="flex flex-col">
                        <span className="text-sm">Imagen de referencia (JPEG, PNG, HEIC) *</span>
                        <input
                            type="file"
                            accept=".jpg,.jpeg,.png,.heic,.heif,image/*"
                            onChange={handleFile}
                            className="mt-2 block w-full cursor-pointer rounded-md border border-white/10 bg-white/5 px-4 py-3 text-sm text-white file:mr-4 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-1 file:text-white hover:bg-white/3"
                        />
                        {errors.imagen && <small className="text-rose-400">{errors.imagen}</small>}
                    </label>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                        <button
                            type="button"
                            disabled={!file}
                            onClick={handleOpenInNewWindow}
                            className="rounded-md border border-white/10 px-2 py-1 text-xs text-gray-200 disabled:opacity-40"
                        >
                            Abrir en el navegador
                        </button>
                        <span className="text-xs text-gray-400">
                            {file ? 'Imagen lista para revisar en otra pestaña.' : 'No se ha seleccionado ninguna imagen.'}
                        </span>
                    </div>
                </div>
            </div>

            {errors.submit && <div className="text-rose-400">{errors.submit}</div>}

            {/* Botones de acción */}
            <div className="flex items-center gap-3">
                <button
                    type="submit"
                    disabled={submitting || comparing}
                    className="flex flex-1 justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500 disabled:opacity-50"
                >
                    {submitting ? 'Enviando...' : 'Enviar a revisión'}
                </button>

                {/* Botón de comparar: solo se renderiza si el padre lo soporta */}
                {onCompare && (
                    <button
                        type="button"
                        disabled={submitting || comparing}
                        onClick={handleCompare}
                        className="flex flex-1 justify-center rounded-md bg-emerald-600 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-emerald-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500 disabled:opacity-50"
                    >
                        {comparing ? 'Comparando...' : 'Comparar carta'}
                    </button>
                )}
            </div>
        </form>
    )
}
