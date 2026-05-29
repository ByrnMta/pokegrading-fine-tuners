import { useState } from 'react'
import useCards from '../../hooks/cards/useCards'
import { validateCardFields, validateCardFile } from '../../utils/validators/cards'

export default function AddCardForm({ onSuccess = () => { } }) {
    const { addCard } = useCards()
    const [form, setForm] = useState({ set_name: '', numero: '', edicion: '', idioma: '', acabado: '' })
    const [file, setFile] = useState(null)
    const [errors, setErrors] = useState({})
    const [submitting, setSubmitting] = useState(false)

    // Validación de campos antes de enviar al servidor, muestra advertencia para cada campo
    const validateFields = () => validateCardFields(form, file)

    // Maneja la selección del archivo, valida formato, tamaño y resolución, y actualiza el estado de errores o del archivo
    const handleFile = async (ev) => {
        const f = ev.target.files?.[0] || null
        setFile(null)
        setErrors((e) => ({ ...e, imagen: undefined }))
        if (!f) return
        
        const validation = validateCardFile(f)
        if (!validation.ok) {
            setErrors((e) => ({ ...e, imagen: validation.error }))
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
            fd.append('numero', form.numero)
            fd.append('set_name', form.set_name)
            fd.append('edicion', form.edicion)
            fd.append('idioma', form.idioma)
            fd.append('acabado', form.acabado)
            fd.append('imagen', file)

            // Envía la solicitud al backend para crear la carta, maneja la respuesta y errores
            const res = await addCard(fd)
            if (!res.ok) {
                setErrors(res.errors || { submit: 'Error de validacion' })
                return
            }
            onSuccess(res.data)
            setForm({ set_name: '', numero: '', edicion: '', idioma: '', acabado: '' })
            setFile(null)
        } catch (err) {
            setErrors({ submit: 'Ocurrio un error inesperado' })
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
                        <input name="set_name" value={form.set_name} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.set_name && <small className="text-rose-400">{errors.set_name}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Número *</span>
                            <input name="numero" value={form.numero} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                            {errors.numero && <small className="text-rose-400">{errors.numero}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Edición *</span>
                        <input name="edicion" value={form.edicion} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.edicion && <small className="text-rose-400">{errors.edicion}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Idioma *</span>
                        <input name="idioma" value={form.idioma} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.idioma && <small className="text-rose-400">{errors.idioma}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Acabado *</span>
                        <input name="acabado" value={form.acabado} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.acabado && <small className="text-rose-400">{errors.acabado}</small>}
                    </label>
                </div>

                <div>
                    <label className="flex flex-col">
                        <span className="text-sm">Imagen de referencia (JPEG, PNG, HEIC) *</span>
                        <input type="file" accept=".jpg,.jpeg,.png,.heic,.heif,image/*" onChange={handleFile} className="mt-2 block w-full cursor-pointer rounded-md border border-white/10 bg-white/5 px-4 py-3 text-sm text-white file:mr-4 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-1 file:text-white hover:bg-white/3" />
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

            <div className="flex items-center gap-2">
                <button disabled={submitting} className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
                    {submitting ? 'Guardando...' : 'Crear carta'}
                </button>
            </div>

        </form>
    )
}
