import AuthFormContainer from './AuthFormContainer'
import useAuth from '../../hooks/auth/useAuth'
import { useState } from 'react'

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
    const [error, set_error] = useState(null)

    const handle_submit = async (event) => {
        event.preventDefault()
        set_error(null)
        set_loading(true)

        // Se obtienen los datos del formulario
        try {
            const form = new FormData(event.target)
            const correo = form.get('correo')
            const nombre_usuario = form.get('nombre_usuario')
            const contrasena = form.get('contrasena')
            const confirm_password = form.get('confirm_password')

            // Validacion basica de contraseñas
            if (contrasena !== confirm_password) {
                set_error('Las contraseñas no coinciden')
                set_loading(false)
                return
            }

            // Llamada al servicio de registro
            await register({ nombre_usuario, correo, contrasena })
            
            // Se redirige al inicio de sesión
            on_switch('login')

        // Manejo de errores con preferencia a mensajes detallados del backend
        } catch (err) {
            set_error(err?.data?.message || err?.data?.detail || err?.message || 'Error al registrar la cuenta')
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
                    </div>
                </div>

                <div>
                    <label htmlFor="nombre_usuario" className="block text-sm/6 font-medium text-gray-100">
                        Nombre de usuario
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
                    </div>
                </div>

                <div>
                    <button type="submit" className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
                        {loading ? 'Registrando...' : 'Registrar cuenta'}
                    </button>
                </div>
                {error && <p className="text-sm text-red-400">{error}</p>}
            </form>
        </AuthFormContainer>
    )
}
