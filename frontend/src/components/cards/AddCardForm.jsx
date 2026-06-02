import { useState } from 'react'
import useCards from '../../hooks/cards/useCards'
import { CANONICAL_RARITIES, SUPPORTED_LANGUAGES, VALID_TYPES, validateCardFields, validateCardFile } from '../../utils/validators/cards'

export default function AddCardForm({ onSuccess = () => { } }) {
    const { addCard } = useCards()
    const [form, setForm] = useState({
        set_name: '',
        numero: '',
        edicion: '',
        idioma: '',
        acabado: '',
        autor: '',
        nombre: '',
        rareza: '',
        tipo: '',
        hp: '',
        ilustrador: '',
        anio_impresion: ''
    })
    const [frontFile, setFrontFile] = useState(null)
    const [backFile, setBackFile] = useState(null)
    const [errors, setErrors] = useState({})
    const [submitting, setSubmitting] = useState(false)

    // Validación de campos antes de enviar al servidor, muestra advertencia para cada campo
    const validateFields = () => validateCardFields(form, frontFile, backFile)

    // Maneja la selección del archivo, valida formato, tamaño y resolución, y actualiza el estado de errores o del archivo
    const handleFile = async (ev, side) => {
        const f = ev.target.files?.[0] || null
        if (side === 'front') {
            setFrontFile(null)
            setErrors((e) => ({ ...e, imagen_frontal: undefined }))
        } else {
            setBackFile(null)
            setErrors((e) => ({ ...e, imagen_reverso: undefined }))
        }
        if (!f) return
        
        const validation = validateCardFile(f)
        if (!validation.ok) {
            setErrors((e) => ({
                ...e, [side === 'front' ? 'imagen_frontal' : 'imagen_reverso']: validation.error
            }))
            return
        }
        if (side === 'front') {
            setFrontFile(f)
        } else {
            setBackFile(f)
        }
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
            fd.append('autor', form.autor)
            if (form.nombre) fd.append('nombre', form.nombre)
            if (form.rareza) fd.append('rareza', form.rareza)
            if (form.tipo) fd.append('tipo', form.tipo)
            if (form.hp) fd.append('hp', form.hp)
            if (form.ilustrador) fd.append('ilustrador', form.ilustrador)
            if (form.anio_impresion) fd.append('anio_impresion', form.anio_impresion)
            fd.append('imagen_frontal', frontFile)
            fd.append('imagen_reverso', backFile)

            // Envía la solicitud al backend para crear la carta, maneja la respuesta y errores
            const res = await addCard(fd)
            if (!res.ok) {
                setErrors(res.errors || { submit: 'Error de validacion' })
                return
            }
            onSuccess(res.data)
            setForm({
                set_name: '',
                numero: '',
                edicion: '',
                idioma: '',
                acabado: '',
                autor: '',
                nombre: '',
                rareza: '',
                tipo: '',
                hp: '',
                ilustrador: '',
                anio_impresion: ''
            })
            setFrontFile(null)
            setBackFile(null)
        } catch (err) {
            setErrors({ submit: 'Ocurrio un error inesperado' })
        } finally {
            setSubmitting(false)
        }
    }

    // Función para abrir la imagen seleccionada en una nueva pestaña del navegador
    const handleOpenInNewWindow = (side) => {
        const targetFile = side === 'front' ? frontFile : backFile
        if (!targetFile) return
        const url = URL.createObjectURL(targetFile)
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
                        <select
                            name="idioma"
                            value={form.idioma}
                            onChange={handleChange}
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        >
                            <option value="">Selecciona un idioma</option>
                            {SUPPORTED_LANGUAGES.map((language) => (
                                <option key={language} value={language}>
                                    {language.toUpperCase()}
                                </option>
                            ))}
                        </select>
                        {errors.idioma && <small className="text-rose-400">{errors.idioma}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Acabado *</span>
                        <input name="acabado" value={form.acabado} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.acabado && <small className="text-rose-400">{errors.acabado}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Autor *</span>
                        <input name="autor" value={form.autor} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.autor && <small className="text-rose-400">{errors.autor}</small>}
                    </label>



                    <div className="pt-4 border-t border-white/10">
                        <h3 className="text-sm font-semibold text-gray-100/75 text-center">Display de la carta (opcional)</h3>
                    </div>

                    <label className="flex flex-col">
                        <span className="text-sm">Nombre</span>
                        <input name="nombre" value={form.nombre} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.nombre && <small className="text-rose-400">{errors.nombre}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Rareza</span>
                        <select
                            name="rareza"
                            value={form.rareza}
                            onChange={handleChange}
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        >
                            <option value="">Selecciona una rareza</option>
                            {CANONICAL_RARITIES.map((rarity) => (
                                <option key={rarity} value={rarity}>
                                    {rarity}
                                </option>
                            ))}
                        </select>
                        {errors.rareza && <small className="text-rose-400">{errors.rareza}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Tipo</span>
                        <select
                            name="tipo"
                            value={form.tipo}
                            onChange={handleChange}
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        >
                            <option value="">Selecciona un tipo</option>
                            {VALID_TYPES.map((type) => (
                                <option key={type} value={type}>
                                    {type}
                                </option>
                            ))}
                        </select>
                        {errors.tipo && <small className="text-rose-400">{errors.tipo}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">HP</span>
                        <input name="hp" value={form.hp} onChange={handleChange} inputMode="numeric" className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.hp && <small className="text-rose-400">{errors.hp}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Ilustrador</span>
                        <input name="ilustrador" value={form.ilustrador} onChange={handleChange} className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.ilustrador && <small className="text-rose-400">{errors.ilustrador}</small>}
                    </label>

                    <label className="flex flex-col">
                        <span className="text-sm">Año de impresion</span>
                        <input name="anio_impresion" value={form.anio_impresion} onChange={handleChange} inputMode="numeric" className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6" />
                        {errors.anio_impresion && <small className="text-rose-400">{errors.anio_impresion}</small>}
                    </label>
                </div>

                <div className="pt-4 border-t border-white/10"></div>


                <div>
                    <label className="flex flex-col">
                        <span className="text-sm">Imagen de referencia (frente) (JPEG, PNG, HEIC) *</span>
                        <input type="file" accept=".jpg,.jpeg,.png,.heic,.heif,image/*" onChange={(ev) => handleFile(ev, 'front')} className="mt-2 block w-full cursor-pointer rounded-md border border-white/10 bg-white/5 px-4 py-3 text-sm text-white file:mr-4 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-1 file:text-white hover:bg-white/3" />
                        {errors.imagen_frontal && <small className="text-rose-400">{errors.imagen_frontal}</small>}
                    </label>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                        <button
                            type="button"
                            disabled={!frontFile}
                            onClick={() => handleOpenInNewWindow('front')}
                            className="rounded-md border border-white/10 px-2 py-1 text-xs text-gray-200 disabled:opacity-40"
                        >
                            Abrir en el navegador
                        </button>
                        <span className="text-xs text-gray-400">
                            {frontFile ? 'Imagen lista para revisar en otra pestaña.' : 'No se ha seleccionado ninguna imagen.'}
                        </span>
                    </div>
                </div>

                <div>
                    <label className="flex flex-col">
                        <span className="text-sm">Imagen de referencia (reverso) (JPEG, PNG, HEIC) *</span>
                        <input type="file" accept=".jpeg,.png,.heic,image/*" onChange={(ev) => handleFile(ev, 'back')} className="mt-2 block w-full cursor-pointer rounded-md border border-white/10 bg-white/5 px-4 py-3 text-sm text-white file:mr-4 file:rounded-md file:border-0 file:bg-white/10 file:px-3 file:py-1 file:text-white hover:bg-white/3" />
                        {errors.imagen_reverso && <small className="text-rose-400">{errors.imagen_reverso}</small>}
                    </label>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                        <button
                            type="button"
                            disabled={!backFile}
                            onClick={() => handleOpenInNewWindow('back')}
                            className="rounded-md border border-white/10 px-2 py-1 text-xs text-gray-200 disabled:opacity-40"
                        >
                            Abrir en el navegador
                        </button>
                        <span className="text-xs text-gray-400">
                            {backFile ? 'Imagen lista para revisar en otra pestaña.' : 'No se ha seleccionado ninguna imagen.'}
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
