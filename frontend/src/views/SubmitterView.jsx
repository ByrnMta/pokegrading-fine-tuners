import SubmitterNavbar from '../components/submitter/SubmitterNavbar'
import SubmitterCardForm from '../components/submitter/SubmitterCardForm'

/**
 * Vista principal para usuarios submitter.
 *
 * Flujo:
 * 1. Carga de imagen frontal y reverso.
 * 2. Comparación opcional contra la base de datos (búsqueda rápida).
 * 3. Envío de carta → el backend corre el pipeline completo
 *    (preprocesamiento + calificación) y devuelve el resultado de grading.
 * 4. Visualización del resultado: subgrades, grado final, banda de
 *    incertidumbre, baseline y versión del algoritmo.
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
                            Enviar carta para evaluación
                        </h1>

                        <p className="mt-2 text-sm text-gray-400">
                            Sube las imágenes frontal y reverso. Al enviar, la carta se procesará y calificará automáticamente.
                        </p>
                    </header>

                    <SubmitterCardForm />
                </section>
            </main>
        </div>
    )
}
