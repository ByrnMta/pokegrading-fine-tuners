import { useLocation } from 'react-router-dom'
import Navbar from '../components/cards/Navbar'
import AddCardForm from '../components/cards/AddCardForm'

export default function AdminView() {
    const { pathname } = useLocation()
    const isCards = pathname === '/admin/cards'
    const title = isCards ? 'Agregar carta' : 'Catálogo de cartas'

    const sectionClassName =
        isCards
            ? 'mx-auto max-w-2xl rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20'
            : 'rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20'

    return (
        <div>
            <Navbar />
            <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <section className={sectionClassName}>
                    <h1 className="mt-2 text-2xl font-semibold text-white underline">{title}</h1>

                    {isCards && (
                        <div className="mt-6">
                            <AddCardForm onSuccess={(res) => console.log('Card created', res)} />
                        </div>
                    )}
                </section>
            </main>
        </div>
    )
}
