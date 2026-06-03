import { useNavigate } from 'react-router-dom'
import useAuth from '../../hooks/auth/useAuth'

/**
 * Navbar exclusivo para la vista Submitter.
 *
 * No incluye rutas administrativas para mantener separado el flujo
 * de usuarios submitter del flujo de administradores.
 *
 * @returns {JSX.Element}
 */
export default function SubmitterNavbar() {
    const { logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <nav className="relative bg-gray-800/50 shadow-md after:pointer-events-none after:absolute after:inset-x-0 after:bottom-0 after:h-px after:bg-white/10">
            <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
                <div className="flex flex-col gap-3 py-3 sm:flex-row sm:items-center sm:justify-between">

                    <div className="flex items-center gap-3">
                        <div className="flex shrink-0 items-center">
                            <img
                                src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500"
                                alt="PokeGrading UI"
                                className="h-8 w-auto"
                            />
                        </div>

                        <div className="flex flex-col">
                            <span className="text-sm font-semibold text-white">
                                PokeGrading
                            </span>
                            <span className="text-xs text-gray-400">
                                Vista Submitter
                            </span>
                        </div>
                    </div>

                    <div className="flex items-center">
                        <button
                            type="button"
                            onClick={handleLogout}
                            className="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-white/5 hover:text-white cursor-pointer border border-white/10 shadow-md/20"
                        >
                            Cerrar sesión
                        </button>
                    </div>

                </div>
            </div>
        </nav>
    )
}