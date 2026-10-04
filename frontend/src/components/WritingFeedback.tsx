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
    {correction.grammar_check && <div className="mt-4 space-y-3">
      <h4 className="font-bold">Gramática A2 · {correction.grammar_check.issues.length} ajuste(s) detectado(s)</h4>
      {correction.grammar_check.issues.map(issue => <div key={`${issue.start}-${issue.rule}`} className="rounded-xl border border-slate-500 p-3">
        <p className="font-bold">{issue.original} → {issue.replacement}{issue.unit && <span className="ml-2 text-xs">Unidad {issue.unit}</span>}</p><p className="mt-1">{issue.explanation}</p>
        {issue.references.map(ref => <details key={`${ref.source}-${ref.page}`} className="mt-2 break-words"><summary className="cursor-pointer">Ejemplo del libro · página PDF {ref.page}</summary><p className="mt-2">{ref.source}</p><blockquote className="mt-1">«{ref.excerpt}»</blockquote><p className={`mt-1 text-xs ${muted}`}>Texto reconocido del libro; puede contener errores de lectura.</p></details>)}
      </div>)}
      <p className={`text-xs ${muted}`}>Comprobamos estructuras seleccionadas de las diez unidades A2. No detectar errores no garantiza que todo el texto sea correcto.</p>
      {correction.grammar_check.units && <details><summary className="cursor-pointer">¿Qué comprobamos en A2?</summary><ul className="mt-2 list-inside list-disc">{correction.grammar_check.units.map(unit => <li key={unit}>{unit}</li>)}</ul></details>}
      {['unavailable', 'rejected'].includes(correction.grammar_check.model_status) && <p>Solo se ha podido completar la comprobación de las estructuras A2. Puedes volver a intentar la revisión general.</p>}
    </div>}
    {correction.status === 'partial' && correction.skipped > 0 && <p className="mt-3 font-semibold">Revisión parcial: {correction.skipped} frase(s) sin revisar. Prueba con frases más cortas.</p>}
    <p className={`mt-3 text-xs ${muted}`}>El revisor puede pasar por alto errores. Comprueba que los cambios conservan lo que querías decir; no son una calificación del contenido.</p>
  </section>
}
