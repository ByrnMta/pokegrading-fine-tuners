import AuthFormContainer from './AuthFormContainer'
import useAuth from '../../hooks/auth/useAuth'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

/** * Formulario de inicio de sesión.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {(target: 'login' | 'register') => void} [props.on_switch] - Alternar entre vistas de auth.
 * @return {JSX.Element} Componente de formulario de inicio de sesión.
 */
export default function LoginForm({ on_switch = () => { } }) {
    const { login } = useAuth()
    const [loading, set_loading] = useState(false)
    const [errors, set_errors] = useState({})
    const navigate = useNavigate()

    // Función para manejar el envío del formulario de inicio de sesión
    const handle_submit = async (event) => {
        event.preventDefault()
        set_errors({})
        set_loading(true)

        // Se obtienen los datos del formulario
        try {
            const form = new FormData(event.target)
            const correo = form.get('correo')
            const contrasena = form.get('contrasena')

            // Llamada al servicio de inicio de sesión
            const res = await login({ correo, contrasena })
            if (!res.ok) {
                set_errors(res.errors || { form: 'Error en el inicio de sesion' })
                return
            }
            // Mostrar mensaje de éxito

            // Se redirige a la página principal

        } catch (err) {
            set_errors({ form: 'Ocurrio un error inesperado' })
        } finally {
            set_loading(false)
        }
    }

    return (
        <AuthFormContainer
            title="Iniciar sesion con tu cuenta de PokeGrading"
            switch_label="Aun no tienes una cuenta?"
            switch_action_text="Registrarte aqui"
            switch_target="register"
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
                            autoComplete="current-password"
                            placeholder="••••••••"
                            className="block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"
                        />
                        {errors.contrasena && <small className="text-red-400">{errors.contrasena}</small>}
                    </div>
                </div>

                <div>
                    <button type="submit" className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
                        {loading ? 'Ingresando...' : 'Iniciar sesion'}
                    </button>

                </div>
                {errors.form && <p className="text-sm text-red-400">{errors.form}</p>}
            </form>

            <button type="button" onClick={() => navigate('/admin')} className="flex w-full justify-center mt-2 rounded-md bg-gray-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-gray-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
                Ingresar como administrador (para pruebas)
            </button>
            
        </AuthFormContainer>
    )
}
