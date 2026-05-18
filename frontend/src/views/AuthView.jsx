import { useState } from 'react'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'

/**
 * Vista para autenticacion (login y registro).
 * Controla el cambio entre formularios mediante un estado local
 *
 * @returns {JSX.Element}
 */
export default function AuthView() {
    const [auth_view, set_auth_view] = useState('login')

    const handle_switch_view = (target_view) => {
        set_auth_view(target_view)
    }

    return auth_view === 'login' ? (
        <LoginForm on_switch={handle_switch_view} />
    ) : (
        <RegisterForm on_switch={handle_switch_view} />
    )
}
