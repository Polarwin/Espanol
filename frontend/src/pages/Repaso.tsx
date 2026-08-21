import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { ReviewItem, ReviewResult } from '../api/types'
import { AudioPlayer } from '../components/AudioPlayer'
import { IconCheck, IconReplay } from '../components/icons'

const LABELS: Record<string, string> = {
  vocabulary: 'Vocabulario', grammar: 'Gramática', listening: 'Comprensión auditiva',
  reading: 'Comprensión lectora', writing: 'Escritura', pronunciation: 'Pronunciación',
}

export function Repaso() {
  const [items, setItems] = useState<ReviewItem[]>([])
  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<ReviewResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [checking, setChecking] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getReviewItems().then(setItems).catch(() => setError('No se pudieron cargar tus errores.')).finally(() => setLoading(false))
  }, [])

  const item = items[index]
  const check = async () => {
    if (!item || !answer.trim() || checking) return
    setChecking(true); setError('')
    try { setResult(await api.answerReview(item.id, answer.trim())) }
    catch { setError('No se pudo guardar el repaso. Inténtalo otra vez.') }
    finally { setChecking(false) }
  }
  const next = () => { setIndex((value) => value + 1); setAnswer(''); setResult(null) }

  if (loading) return <div className="p-6 font-semibold text-ink-soft">Preparando tus errores…</div>
  if (!item && error) return <div className="mx-auto max-w-xl px-4 py-10 sm:px-8"><div className="rounded-3xl bg-blush p-7 text-center shadow-soft" role="alert"><span className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-terracotta text-paper"><IconReplay size={26} /></span><h1 className="mt-4 font-display text-3xl font-bold">No pudimos cargar tu repaso</h1><p className="mt-2 font-semibold text-terracotta">{error}</p></div></div>
  if (!item) return <div className="mx-auto max-w-xl px-4 py-10 sm:px-8"><div className="rounded-3xl bg-leaf-soft p-7 text-center shadow-soft"><span className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-leaf text-paper"><IconCheck size={26} /></span><h1 className="mt-4 font-display text-3xl font-bold">¡Repaso al día!</h1><p className="mt-2 font-semibold text-ink-soft">{items.length ? 'Has repasado todos los errores de hoy.' : 'Cuando tengas una respuesta incorrecta, aparecerá aquí para practicarla.'}</p></div></div>

  return <div className="mx-auto max-w-2xl px-4 py-7 sm:px-8 sm:py-10">
    <div className="flex items-center gap-3"><span className="flex h-12 w-12 items-center justify-center rounded-full bg-blush text-terracotta"><IconReplay size={22} /></span><div><p className="text-xs font-extrabold uppercase tracking-wider text-terracotta">Repasa tus errores</p><h1 className="font-display text-3xl font-bold">Otra oportunidad</h1></div></div>
    <section className="mt-6 rounded-3xl bg-paper p-5 shadow-card sm:p-7">
      <div className="flex justify-between text-sm font-bold text-ink-soft"><span>{LABELS[item.kind] ?? item.kind}</span><span>{index + 1} de {items.length}</span></div>
      {item.passage && <div className="mt-5 rounded-2xl bg-cream p-4 font-semibold leading-relaxed text-ink-soft">{item.passage}</div>}
      {item.audio_url && <div className="mt-5"><AudioPlayer src={item.audio_url} /></div>}
      <h2 className="mt-6 font-display text-2xl font-bold">{item.prompt}</h2>
      {item.options ? <div className="mt-4 grid gap-2">{item.options.map((option) => <button key={option} disabled={Boolean(result) || checking} onClick={() => setAnswer(option)} className={`rounded-2xl border-2 px-4 py-3 text-left font-semibold ${answer === option ? 'border-river bg-river-soft' : 'border-ink/10'}`}>{option}</button>)}</div> : <textarea rows={3} disabled={Boolean(result) || checking} value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Escribe tu respuesta…" className="mt-4 w-full rounded-2xl border-2 border-ink/10 px-4 py-3 outline-none focus:border-river" />}
      {result && <div className={`mt-4 rounded-2xl p-4 font-semibold ${result.correct ? 'bg-leaf-soft text-leaf' : 'bg-blush text-terracotta'}`}><p className="font-bold">{result.feedback}</p>{!result.correct && <p className="mt-1 text-sm">Vuelve mañana: este punto seguirá en tu repaso.</p>}{result.correct && <p className="mt-1 text-sm">¡Bien! Volverá más adelante para confirmar que lo recuerdas.</p>}</div>}
      {error && <p className="mt-4 font-bold text-terracotta" role="alert">{error}</p>}
      <button disabled={!answer.trim() || checking} onClick={result ? next : () => void check()} className="mt-5 w-full rounded-2xl bg-terracotta py-3 font-bold text-paper disabled:opacity-40">{checking ? 'Comprobando…' : result ? (index + 1 === items.length ? 'Terminar' : 'Siguiente error') : 'Comprobar'}</button>
    </section>
  </div>
}
