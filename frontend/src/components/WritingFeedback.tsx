import type { WritingCorrection } from '../api/types'

export function WritingFeedback({ correction }: { correction?: WritingCorrection | null }) {
  if (!correction) return null
  const changed = correction.suggested && correction.suggested !== correction.original
  return <section className="mt-4 rounded-2xl bg-river-soft p-4 text-sm" aria-live="polite">
    <h3 className="font-bold text-river">Sugerencias de escritura</h3>
    {correction.status === 'unavailable' ? <p className="mt-2">La revisión no está disponible ahora. Tu respuesta se ha guardado.</p> : <>
      {changed ? <><p className="mt-2 font-bold">Tu respuesta</p><p className="whitespace-pre-wrap">{correction.original}</p><p className="mt-3 font-bold">Propuesta para practicar</p><p className="whitespace-pre-wrap">{correction.suggested}</p><p className="mt-2 text-ink-soft">Compara las versiones y comprueba que la propuesta conserva lo que querías decir.</p></> : <p className="mt-2">No se han propuesto cambios. Esto no garantiza que todos los usos sean correctos.</p>}
      {correction.status === 'partial' && <p className="mt-2 font-semibold">Revisión parcial: {correction.skipped} frase(s) sin revisar. Prueba con frases más cortas.</p>}
    </>}
    <p className="mt-2 text-xs text-ink-soft">Son sugerencias, no una calificación del contenido.</p>
  </section>
}
