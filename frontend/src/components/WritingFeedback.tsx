import type { WritingCorrection } from '../api/types'
import { correctionKind, visibleSpaces, writingDiff } from './writingDiff'

export function WritingFeedback({ correction, dark = false }: { correction?: WritingCorrection | null; dark?: boolean }) {
  if (!correction) return null
  const unavailable = correction.status === 'unavailable' || correction.suggested === null
  const kind = correctionKind(correction.original, correction.suggested ?? correction.original)
  const muted = dark ? 'text-slate-300' : 'text-ink-soft'
  return <section className={`mt-4 rounded-2xl p-4 text-sm ${dark ? 'bg-slate-900 text-white' : 'bg-river-soft text-ink'}`} aria-live="polite">
    <h3 className={`font-bold ${dark ? 'text-lime-200' : 'text-river'}`}>{unavailable ? 'Revisión no disponible' : kind === 'spacing' ? 'Solo un ajuste de espacios' : kind === 'unchanged' ? 'Sin cambios propuestos' : 'Cambios propuestos para revisar'}</h3>
    {unavailable ? <p className="mt-2">No se pudo revisar el texto. Vuelve a intentarlo.</p> : <>
      {kind === 'unchanged' ? <p className="mt-2">El revisor no ha propuesto cambios. Esto no garantiza que todos los usos sean correctos.</p> : <>
        {kind === 'spacing' && <p className="mt-2">La propuesta solo cambia espacios; no modifica palabras ni signos de puntuación.</p>}
        <p className={`mt-3 text-xs ${muted}`}>Tachado: se quita. Resaltado: se añade. ␠ indica un espacio.</p>
        <p className="mt-3 whitespace-pre-wrap break-words leading-7" aria-label="Texto con cambios marcados">{writingDiff(correction.original, correction.suggested!).map((edit, index) => edit.kind === 'same'
          ? <span key={index}>{edit.text}</span>
          : edit.kind === 'removed'
            ? <del key={index} className={`mx-0.5 rounded px-0.5 ${dark ? 'bg-rose-950 text-rose-200' : 'bg-rose-100 text-rose-900'}`} aria-label={`Se elimina: ${visibleSpaces(edit.text)}`}>{visibleSpaces(edit.text)}</del>
            : <ins key={index} className={`mx-0.5 rounded px-0.5 font-bold no-underline ${dark ? 'bg-emerald-950 text-emerald-200' : 'bg-emerald-100 text-emerald-900'}`} aria-label={`Se añade: ${visibleSpaces(edit.text)}`}>{visibleSpaces(edit.text)}</ins>)}</p>
        <details className="mt-3"><summary className={`cursor-pointer font-semibold ${dark ? 'text-lime-200' : 'text-river'}`}>Ver propuesta completa sin marcas</summary><p className="mt-2 whitespace-pre-wrap break-words">{correction.suggested}</p></details>
      </>}
    </>}
    {correction.status === 'partial' && <p className="mt-3 font-semibold">Revisión parcial: {correction.skipped} frase(s) sin revisar. Prueba con frases más cortas.</p>}
    <p className={`mt-3 text-xs ${muted}`}>El revisor puede pasar por alto errores. Comprueba que los cambios conservan lo que querías decir; no son una calificación del contenido.</p>
  </section>
}
