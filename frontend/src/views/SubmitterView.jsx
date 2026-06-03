import SubmitterNavbar from '../components/submitter/SubmitterNavbar'
import SubmitterCardForm from '../components/submitter/SubmitterCardForm'

/**
 * Vista principal para usuarios submitter.
 *
 * Flujo esperado:
 * - Carga de imagen frontal y reverso.
 * - Comparación contra la base de datos.
 * - Visualización de hasta 3 candidatos.
 * - Selección de candidato.
 * - Autorellenado o edición manual de metadata.
 * - Envío final de la carta.
 *
 *
 * @returns {JSX.Element}
 */
export default function SubmitterView() {
    return (
        <div className="min-h-screen bg-gray-950 text-white">
            <SubmitterNavbar />

            <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
                <section className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20">
                    <header className="mb-6">
                        <h1 className="text-2xl font-semibold text-white underline">
                            Enviar carta para comparación
                        </h1>

                        <p className="mt-2 text-sm text-gray-400">
                            Sube las imágenes frontal y reverso de la carta para buscar coincidencias en la base de datos.
                        </p>
                    </header>

                    <SubmitterCardForm />
                </section>
            </main>
        </div>
    )
}