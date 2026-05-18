/**
 * Contenedor para vistas de autenticacion.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {string} props.title - Titulo principal del formulario.
 * @param {React.ReactNode} props.children - Contenido principal del formulario.
 * @param {string} props.switch_label - Texto previo al enlace de cambio de vista.
 * @param {string} props.switch_action_text - Texto clickeable para cambiar de vista.
 * @param {'login' | 'register'} props.switch_target - Vista objetivo al cambiar.
 * @param {(target: 'login' | 'register') => void} [props.on_switch] - Callback al cambiar de vista.
 * @returns {JSX.Element}
 */
export default function AuthFormContainer({
    title,
    children,
    switch_label,
    switch_action_text,
    switch_target,
    on_switch = () => { },
}) {
    const handle_switch = (event) => {
        event.preventDefault()
        on_switch(switch_target)
    }

    return (
        <div className="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-sm">
                <img
                    alt="PokeGrading UI"
                    src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500"
                    className="mx-auto h-10 w-auto"
                />
                <h2 className="mt-10 text-center text-2xl/9 font-bold tracking-tight text-white">
                    {title}
                </h2>
            </div>

            <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                {children}

                <p className="mt-10 text-center text-sm/6 text-gray-400">
                    {switch_label}{' '}
                    <a
                        onClick={handle_switch}
                        className="cursor-pointer font-semibold text-indigo-400 hover:text-indigo-300 hover:underline"
                    >
                        {switch_action_text}
                    </a>
                </p>
            </div>
        </div>
    )
}
