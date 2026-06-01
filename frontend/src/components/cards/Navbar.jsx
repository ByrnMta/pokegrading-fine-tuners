
import { NavLink, useNavigate } from 'react-router-dom'
import useAuth from '../../hooks/auth/useAuth'

const navigationItems = [
    { to: '/admin', label: 'Catálogo de cartas' },
    { to: '/admin/cards', label: 'Agregar carta' },
    { to: '/submit', label: 'Submit' },
]

export default function Navbar() {
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
                            <img src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500" alt="Your Company" className="h-8 w-auto" />
                        </div>
                        <div className="flex flex-1 flex-wrap gap-2">
                            {navigationItems.map((item) => (
                                <NavLink
                                    key={item.to}
                                    to={item.to}
                                    className={({ isActive }) =>
                                        isActive
                                            ? 'rounded-md bg-gray-950/50 px-3 py-2 text-sm font-medium text-white border-b border-white/10'
                                            : 'rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-white/5 hover:text-white cursor-pointer border border-white/10 shadow-md/20'
                                    }

                                >
                                    {item.label}
                                </NavLink>
                            ))}
                        </div>
                    </div>

                    <div className="flex items-center">
                            <button type="button" onClick={handleLogout} className="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-white/5 hover:text-white cursor-pointer border border-white/10 shadow-md/20">
                            Cerrar sesión
                        </button>
                    </div>

                </div>
            </div>
        </nav>

    )
}
