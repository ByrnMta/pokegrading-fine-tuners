import { useState } from 'react'
import { postCard } from '../../services/cards/api_cards'

const ALLOWED_EXT = ['jpeg', 'png', 'heic']

// Función auxiliar para obtener la extensión del archivo
function getExt(name) {
    return String(name).split('.').pop().toLowerCase()
}

export default function AddCardForm({ onSuccess = () => { } }) {
    const [form, setForm] = useState({ set: '', number: '', edition: '', language: '', finish: '' })
    const [file, setFile] = useState(null)
    const [errors, setErrors] = useState({})
    const [submitting, setSubmitting] = useState(false)

    // Validación de campos antes de enviar al servidor, muestra advertencia para cada campo
    const validateFields = () => {
        const err = {}
        if (!form.set) err.set = 'Requerido'
        if (!form.number) err.number = 'Requerido'
        if (!form.edition) err.edition = 'Requerido'
        if (!form.language) err.language = 'Requerido'
        if (!form.finish) err.finish = 'Requerido'
        if (!file) err.image = 'Debe adjuntar una imagen de referencia'

        if (file) {
            const ext = getExt(file.name)
            if (!ALLOWED_EXT.includes(ext)) {
                err.image = 'Formato no soportado. Use jpeg, png o heic.'
            }
        }

        return err
    }

    // Maneja la selección del archivo, valida formato, tamaño y resolución, y actualiza el estado de errores o del archivo
    const handleFile = async (ev) => {
        const f = ev.target.files?.[0] || null
        setFile(null)
        setErrors((e) => ({ ...e, image: undefined }))
        if (!f) return
        
        // Valida la extension del archivo (formato)
        const ext = getExt(f.name)
        if (!ALLOWED_EXT.includes(ext)) {
            setErrors((e) => ({ ...e, image: 'Formato no soportado. Use jpeg, png o heic.' }))
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
        const fieldErr = validateFields()

        // Si hay errores de validación, no enviar y mostrar errores
        if (Object.keys(fieldErr).length) {
            setErrors(fieldErr)
            return
        }

        // Actualiza el estado a enviando
        setSubmitting(true)

        // Intenta enviar los datos al backend, maneja la respuesta exitosa o muestra errores de envío
        try {
            
            // Obtiene los datos del formulario y el archivo para la solicitud
            const fd = new FormData()
            fd.append('set', form.set)
            fd.append('number', form.number)
            fd.append('edition', form.edition)
            fd.append('language', form.language)
            fd.append('finish', form.finish)
            fd.append('image', file)

            // Envía la solicitud al backend para crear la carta, maneja la respuesta y errores
            const res = await postCard(fd)
            onSuccess(res)
            setForm({ set: '', number: '', edition: '', language: '', finish: '' })
            setFile(null)
        } catch (err) {
            // Genera mensaje de error con preferencia a respuesta del backend, si no muestra mensaje genérico
            const message = err?.data?.message || err?.message || 'Error al crear la carta'
            setErrors({ submit: message })
        } finally {
            setSubmitting(false)
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
                <div className="space-y-3">
                    <label className="flex flex-col">
                        <span className="text-sm">Set *</span>
                        <input name="set" value={form.set} onChange={handleChange} className="mt-1 w-full rounded-md bg-gray-700 px-3 py-2 text-white" />
                        {errors.set && <small className="text-rose-400">{errors.set}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Número *</span>
                        <input name="number" value={form.number} onChange={handleChange} className="mt-1 w-full rounded-md bg-gray-700 px-3 py-2 text-white" />
                        {errors.number && <small className="text-rose-400">{errors.number}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Edición *</span>
                        <input name="edition" value={form.edition} onChange={handleChange} className="mt-1 w-full rounded-md bg-gray-700 px-3 py-2 text-white" />
                        {errors.edition && <small className="text-rose-400">{errors.edition}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Idioma *</span>
                        <input name="language" value={form.language} onChange={handleChange} className="mt-1 w-full rounded-md bg-gray-700 px-3 py-2 text-white" />
                        {errors.language && <small className="text-rose-400">{errors.language}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Acabado *</span>
                        <input name="finish" value={form.finish} onChange={handleChange} className="mt-1 w-full rounded-md bg-gray-700 px-3 py-2 text-white" />
                        {errors.finish && <small className="text-rose-400">{errors.finish}</small>}
                    </label>
                </div>

                <div>
                    <label className="flex flex-col">
                        <span className="text-sm">Imagen de referencia (JPEG, PNG, HEIC) *</span>
                        <input type="file" accept=".jpg,.jpeg,.png,.heic,.heif,image/*" onChange={handleFile} className="mt-2 block w-full cursor-pointer rounded-md border border-white/10 bg-gray-700 px-4 py-3 text-sm text-white file:mr-4 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-1 file:text-white hover:bg-gray-600" />
                        {errors.image && <small className="text-rose-400">{errors.image}</small>}
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

            <div className="flex items-center gap-2">
                <button disabled={submitting} className="rounded bg-indigo-600 px-4 py-2 text-white disabled:opacity-50">{submitting ? 'Guardando...' : 'Crear carta'}</button>
            </div>

        </form>
    )
}
