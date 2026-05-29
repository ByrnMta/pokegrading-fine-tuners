import AuthFormContainer from './AuthFormContainer'
import useAuth from '../../hooks/auth/useAuth'
import { useState } from 'react'
import { REGISTER_COUNTRIES, REGISTER_LANGUAGES, validateRegisterFields } from '../../utils/validators/auth'

/**
 * Formulario de registro de cuenta.
 * 
 * @param {Object} props - Propiedades del componente.
 * @param {(target: 'login' | 'register') => void} [props.on_switch] - Alternar entre vistas de auth.
 * @return {JSX.Element} Componente de formulario de registro.
 */
export default function RegisterForm({ on_switch = () => { } }) {
    const { register } = useAuth()
    const [loading, set_loading] = useState(false)
    const [errors, set_errors] = useState({})

    const handle_submit = async (event) => {
        event.preventDefault()
        set_errors({})
        set_loading(true)

        // Se obtienen los datos del formulario
        try {
            const form = new FormData(event.target)
            const correo = form.get('correo')
            const nombre_usuario = form.get('nombre_usuario')
            const contrasena = form.get('contrasena')
            const confirm_password = form.get('confirm_password')
            const pais = form.get('pais')
            const idioma = form.get('idioma')
            const disclosure = form.get('disclosure') === 'on' // Puede ser string o int, no boolean

            const fieldErrors = validateRegisterFields({
                correo,
                nombre_usuario,
                contrasena,
                confirm_password,
                pais,
                idioma,
                disclosure
            })
            if (Object.keys(fieldErrors).length) {
                set_errors(fieldErrors)
                set_loading(false)
                return
            }

            // Llamada al servicio de registro
            const res = await register({ nombre_usuario, correo, contrasena, pais, idioma, disclosure })
            if (!res.ok) {
                set_errors(res.errors || { form: 'Error al registrar la cuenta' })
                return
            }
            
            // Se redirige al inicio de sesión
            on_switch('login')

        // Manejo de errores con preferencia a mensajes detallados del backend
        } catch (err) {
            set_errors({ form: 'Ocurrio un error inesperado' })
        } finally {
            set_loading(false)
        }
    }

    return (
        <AuthFormContainer
            title="Registrar nueva cuenta en PokeGrading"
            switch_label="Ya tienes una cuenta?"
            switch_action_text="Inicia sesion aqui"
            switch_target="login"
            on_switch={on_switch}
        >
            <form onSubmit={handle_submit} className="space-y-6">
                <div>
                    <label htmlFor="correo" className="block text-sm/6 font-medium text-gray-100">
                        Direccion de correo electronico
                    </label>
                    <div className="mt-2">
                        <input
                            id="correo"
                            name="correo"
                            type="email"
                            required
                            autoComplete="email"
                            placeholder="tu@email.com"
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        />
                        {errors.correo && <small className="text-red-400">{errors.correo}</small>}
                    </div>
                </div>

                <div>
                    <label htmlFor="nombre_usuario" className="block text-sm/6 font-medium text-gray-100">
                        Alias
                    </label>
                    <div className="mt-2">
                        <input
                            id="nombre_usuario"
                            name="nombre_usuario"
                            type="text"
                            required
                            autoComplete="username"
                            placeholder="Tu nombre de usuario"
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        />
                        {errors.nombre_usuario && <small className="text-red-400">{errors.nombre_usuario}</small>}
                    </div>
                </div>

                <div>
                    <label htmlFor="pais" className="block text-sm/6 font-medium text-gray-100">
                        Pais de residencia
                    </label>
                    <div className="mt-2">
                        <select
                            id="pais"
                            name="pais"
                            required
                            defaultValue=""
                            className="cursor-pointer block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        >
                            <option value="" disabled>Selecciona un pais</option>
                            {REGISTER_COUNTRIES.map((country) => (
                                <option key={country} value={country}>{country}</option>
                            ))}
                        </select>
                        {errors.pais && <small className="text-red-400">{errors.pais}</small>}
                    </div>
                </div>

                <div>
                    <label htmlFor="idioma" className="block text-sm/6 font-medium text-gray-100">
                        Idioma preferido
                    </label>
                    <div className="mt-2">
                        <select
                            id="idioma"
                            name="idioma"
                            required
                            defaultValue="es"
                            className="cursor-pointer block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        >
                            {REGISTER_LANGUAGES.map((language) => (
                                <option key={language} value={language}>
                                    {language === 'es' ? 'Espanol' : 'Ingles'}
                                </option>
                            ))}
                        </select>
                        {errors.idioma && <small className="text-red-400">{errors.idioma}</small>}
                    </div>
                </div>

                <div>
                    <div className="flex items-center justify-between">
                        <label htmlFor="contrasena" className="block text-sm/6 font-medium text-gray-100">
                            Contraseña
                        </label>
                    </div>
                    <div className="mt-2">
                        <input
                            id="contrasena"
                            name="contrasena"
                            type="password"
                            required
                            autoComplete="new-password"
                            placeholder="••••••••"
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        />
                        {errors.contrasena && <small className="text-red-400">{errors.contrasena}</small>}
                    </div>
                </div>

                <div>
                    <div className="flex items-center justify-between">
                        <label htmlFor="confirm_password" className="block text-sm/6 font-medium text-gray-100">
                            Confirmar contraseña
                        </label>
                    </div>
                    <div className="mt-2">
                        <input
                            id="confirm_password"
                            name="confirm_password"
                            type="password"
                            required
                            autoComplete="new-password"
                            placeholder="••••••••"
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        />
                        {errors.confirm_password && <small className="text-red-400">{errors.confirm_password}</small>}
                    </div>
                </div>

                <div className="flex items-start gap-3">
                    <input
                        id="disclosure"
                        name="disclosure"
                        type="checkbox"
                        className="cursor-pointer mt-1 size-4 rounded border-white/10 bg-white/5 text-indigo-500 focus:ring-indigo-500"
                    />
                    <label htmlFor="disclosure" className="text-sm text-gray-100/75">
                        Acepto que PokéGrading es informativo y no sustituye PSA, BGS ni CGC.
                    </label>
                </div>
                {errors.disclosure && <small className="text-red-400">{errors.disclosure}</small>}

                <div>
                    <button type="submit" className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
                        {loading ? 'Registrando...' : 'Registrar cuenta'}
                    </button>
                </div>
                {errors.form && <p className="text-sm text-red-400">{errors.form}</p>}
            </form>
        </AuthFormContainer>
    )
}
