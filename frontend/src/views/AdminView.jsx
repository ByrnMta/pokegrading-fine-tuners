import { useState } from 'react'
import Navbar from '../components/cards/Navbar'
import AddCardForm from '../components/cards/AddCardForm'

const sections = {
    catalog: {
        title: 'Catálogo de cartas',
    },
    cards: {
        title: 'Agregar carta',
    },

}

export default function AdminView() {
    const [activeSection, set_activeSection] = useState('catalog')

    const currentSection = sections[activeSection] ?? sections.catalog

    const sectionClassName =
        activeSection === 'cards'
            ? 'mx-auto max-w-2xl rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20'
            : 'rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20'

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            <Navbar activeSection={activeSection} onNavigate={set_activeSection} />

            <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <section className={sectionClassName}>
                    <h1 className="mt-2 text-2xl font-semibold text-white underline">{currentSection.title}</h1>

                    {activeSection === 'cards' && (
                        <div className="mt-6">
                            <AddCardForm onSuccess={(res) => console.log('Card created', res)} />
                        </div>
                    )}
                </section>
            </main>
        </div>
    )
}
