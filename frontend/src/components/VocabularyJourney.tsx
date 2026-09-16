import { useEffect, useRef, useState } from 'react'
import { api, ApiError } from '../api/client'
import type { VocabularyJourney as Journey, VocabularyAction } from '../api/types'

const primary = 'rounded-2xl bg-lime-300 px-6 py-3 font-bold text-slate-950 shadow-lg transition hover:bg-lime-200 active:scale-[0.98] disabled:opacity-50'
const secondary = 'rounded-2xl border border-slate-500 px-4 py-3 font-semibold text-white transition hover:bg-slate-700 disabled:opacity-50'

export function VocabularyJourney() {
  const [journey, setJourney] = useState<Journey | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [pending, setPending] = useState<VocabularyAction | null>(null)
  const lock = useRef(false)
  const [explanation, setExplanation] = useState<Record<string, { definition: string; example: string }>>({})
  const [explaining, setExplaining] = useState('')
  const [extraError, setExtraError] = useState<{ id: string; message: string } | null>(null)
  const [speechError, setSpeechError] = useState('')
  const [revealed, setRevealed] = useState(true)
  const card = useRef<HTMLDivElement>(null)
  const feedback = useRef<HTMLDivElement>(null)

  async function load() {
    try { setJourney(await api.getVocabularyJourney()); setError(''); setPending(null) }
    catch { setError('No se pudo cargar tu progreso. Vuelve a intentarlo.') }
  }
  useEffect(() => { void load() }, [])
  useEffect(() => { setRevealed(true); setSpeechError(''); window.speechSynthesis?.cancel() }, [journey?.word?.id])
  useEffect(() => () => { window.speechSynthesis?.cancel() }, [])

  async function send(command: VocabularyAction) {
    if (lock.current) return
    lock.current = true; setBusy(true); setError(''); setPending(command)
    try {
      setJourney(await api.actVocabularyJourney(command)); setPending(null)
      requestAnimationFrame(() => {
        const target = command.action === 'answer' ? feedback.current : card.current
        target?.focus({ preventScroll: true })
        if (command.action !== 'language') target?.scrollIntoView({
          block: command.action === 'answer' ? 'nearest' : 'start',
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
        })
      })
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        await load()
        setError('Tu progreso cambió en otra ventana. Hemos recuperado el último paso guardado.')
      } else {
        setError('No se pudo guardar este paso. Reintenta para continuar sin perder tu respuesta.')
      }
    } finally { lock.current = false; setBusy(false) }
  }
  function act(action: VocabularyAction['action'], choice?: string) {
    if (!journey || pending || lock.current) return
    void send({ action, choice, revision: journey.revision, request_id: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}` })
  }
  async function explain() {
    if (!journey?.word || explaining) return
    const id = journey.word.id
    setExplaining(id); setExtraError(null)
    try { const value = await api.explainA2Word(id); setExplanation(current => ({ ...current, [id]: value })) }
    catch { setExtraError({ id, message: 'No se pudo preparar el ejemplo. Puedes seguir con la explicación de la tarjeta o intentarlo otra vez.' }) }
    finally { setExplaining('') }
  }
  function speak() {
    if (!journey?.word) return
    if (!('speechSynthesis' in window)) { setSpeechError('Este navegador no ofrece lectura en voz alta.'); return }
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(journey.word.text.replace(/\/a\b/g, ''))
    utterance.lang = 'es-ES'; utterance.rate = 0.85
    utterance.onerror = () => setSpeechError('No se pudo reproducir la palabra en este dispositivo.')
    window.speechSynthesis.speak(utterance)
  }

  if (!journey) return <section id="palabras" className="rounded-3xl bg-slate-800 p-6"><p role="status">{error || 'Preparando tu próxima mini lección…'}</p>{error && <button className={`${primary} mt-3`} onClick={() => void load()}>Reintentar</button>}</section>
  const disabled = busy || !!pending
  const learning = journey.phase === 'learn' && journey.word
  const summary = journey.phase === 'summary'
  const finished = journey.phase === 'complete'
  const progress = journey.completed / journey.chapters * 100
  const extra = journey.word ? explanation[journey.word.id] : null
  return <section id="palabras" className="overflow-hidden rounded-[2rem] border border-slate-700 bg-slate-800 shadow-xl">
    <div className="bg-gradient-to-br from-teal-900 via-slate-800 to-slate-900 px-5 py-6 sm:px-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-lime-300">Tu aventura de vocabulario</p>
        <span className="rounded-full bg-slate-950/50 px-3 py-1 text-xs text-slate-200">{journey.completed} / {journey.chapters} mini lecciones</span>
      </div>
      <h2 className="mt-3 text-3xl font-bold">{journey.mode === 'review' ? 'Una segunda oportunidad' : journey.mode === 'final' ? 'El gran reto de la unidad' : finished ? 'Has recorrido toda la unidad' : journey.title}</h2>
      <p className="mt-2 text-sm text-slate-300">{journey.mode === 'review' ? 'Recuerda cada expresión dos veces. Lo que todavía cueste volverá en otra ronda.' : journey.mode === 'final' ? 'Todas las palabras, mezcladas. Puedes parar y continuar desde aquí otro día.' : 'Un pequeño paso: descubre, recuerda y ponte a prueba.'}</p>
      <div role="progressbar" aria-label="Mini lecciones completadas" aria-valuenow={journey.completed} aria-valuemin={0} aria-valuemax={journey.chapters} className="mt-5 h-2 overflow-hidden rounded-full bg-slate-950/70"><div className="h-full rounded-full bg-lime-300 transition-all motion-reduce:transition-none" style={{ width: `${progress}%` }} /></div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-300"><span>{journey.seen} expresiones presentadas</span><span>{journey.mistakes} por repasar</span><span>{busy ? 'Guardando…' : pending ? 'Pendiente de guardar' : 'Progreso guardado automáticamente'}</span></div>
    </div>

    <div className="p-5 sm:p-8">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm font-bold text-lime-300">{learning ? `DESCUBRE · ${journey.index + 1} de ${journey.total}` : summary ? 'RONDA COMPLETADA' : finished ? 'TU SIGUIENTE PASO' : `${journey.mode === 'chapter' ? 'MINI QUIZ' : 'RETO'} · ${journey.index + 1} de ${journey.total}`}</p>
        <fieldset className="flex gap-3 text-sm"><legend className="sr-only">Idioma de las explicaciones</legend>{(['es', 'en'] as const).map(language => <label key={language} className="flex items-center gap-1.5"><input type="radio" name="journey-language" disabled={disabled || !!journey.feedback} checked={journey.language === language} onChange={() => act('language', language)} />{language === 'es' ? 'Español' : 'English'}</label>)}</fieldset>
      </div>
      <div ref={card} tabIndex={-1} className="scroll-mt-32 outline-none">
        {learning && journey.word && <div className="rounded-3xl border border-slate-600 bg-slate-900 p-6 sm:p-8">
          <div className="mb-6 flex gap-2" aria-label={`Palabra ${journey.index + 1} de ${journey.total}`}>{Array.from({ length: journey.total }, (_, i) => <span key={i} className={`h-1.5 flex-1 rounded-full ${i <= journey.index ? 'bg-lime-300' : 'bg-slate-700'}`} />)}</div>
          <p className="text-4xl font-bold leading-tight sm:text-5xl">{journey.word.text}</p>
          <button className="mt-3 text-sm font-semibold text-teal-200" onClick={speak}>Escuchar pronunciación ↗</button>
          {speechError && <p className="mt-2 text-sm text-orange-200" role="status">{speechError}</p>}
          <div className="mt-5 min-h-16 sm:min-h-24">{revealed ? <p className="text-xl leading-relaxed text-slate-200" lang={journey.language}>{journey.language === 'es' ? journey.word.clue : journey.word.translation}</p> : <p className="text-xl text-slate-300">Sin mirar: ¿qué significa? Dilo con tus palabras.</p>}</div>
          <button className="mt-3 text-sm font-semibold text-lime-300" onClick={() => setRevealed(!revealed)}>{revealed ? 'Ocultar y probar mi memoria' : 'Ver significado otra vez'}</button>
          {extra ? <div className="mt-5 rounded-2xl bg-slate-800 p-4"><p>{extra.definition}</p><p className="mt-2 italic text-teal-200">«{extra.example}»</p><p className="mt-2 text-xs text-slate-400">Ejemplo generado automáticamente; puede contener errores.</p></div> : <button className="mt-5 block text-sm font-bold text-teal-200 disabled:opacity-50" disabled={!!explaining} onClick={() => void explain()}>{explaining === journey.word.id ? 'Preparando tu ejemplo…' : explaining ? 'Terminando el ejemplo anterior…' : 'Explícamelo con un ejemplo en español'}</button>}
          {extraError?.id === journey.word.id && <p className="mt-3 text-sm text-orange-200" role="status">{extraError.message}</p>}
          <p className="mt-6 text-sm text-slate-400">Hazla tuya: piensa en una persona o situación de tu vida relacionada con esta expresión.</p>
          <button className={`${primary} mt-6 w-full sm:w-auto`} disabled={disabled} onClick={() => act('next')}>{journey.index + 1 === journey.total ? '¡Vamos al mini quiz! →' : 'Siguiente palabra →'}</button>
        </div>}

        {journey.question && <div>
          <p className="text-sm text-slate-400">{journey.question.instruction}</p>
          <h3 className="mt-2 text-2xl font-bold leading-snug">{journey.question.prompt}</h3>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">{journey.question.options.map((option, i) => <button key={option.id} disabled={disabled || !!journey.feedback} onClick={() => act('answer', option.id)} className={`flex min-h-20 items-center gap-3 rounded-2xl border p-4 text-left font-semibold transition enabled:hover:border-lime-300 enabled:hover:bg-slate-700 ${journey.feedback?.answer_id === option.id ? 'border-lime-300 bg-lime-300/10' : journey.feedback?.chosen_id === option.id ? 'border-orange-300 bg-orange-300/10' : 'border-slate-600 bg-slate-900'}`}><span aria-hidden="true" className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-700 text-sm text-lime-200">{journey.feedback?.answer_id === option.id ? '✓' : journey.feedback?.chosen_id === option.id ? '↻' : i + 1}</span><span>{option.label}</span></button>)}</div>
          {journey.feedback && <div ref={feedback} tabIndex={-1} className={`mt-5 scroll-mb-28 rounded-2xl border p-5 outline-none ${journey.feedback.correct ? 'border-lime-400/40 bg-lime-300/10' : 'border-orange-300/40 bg-orange-300/10'}`} role="status">
            <p className="text-xl font-bold">{journey.feedback.correct ? '¡Eso es! Bien recordado.' : 'Ya tienes una pista para la próxima.'}</p>
            <p className="mt-2 font-bold">{journey.feedback.word}</p><p className="mt-1">{journey.feedback.meaning}</p>
            {!journey.feedback.correct && <p className="mt-3 text-sm text-orange-100">La guardamos para tu repaso de errores. Lee el significado antes de seguir.</p>}
            <button className={`${primary} mt-4`} disabled={disabled} onClick={() => act('continue')}>Continuar →</button>
          </div>}
        </div>}

        {summary && <div className="rounded-3xl bg-slate-900 p-7 text-center">
          <span aria-hidden="true" className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-lime-300 text-3xl text-slate-950">✓</span>
          <h3 className="mt-5 text-2xl font-bold">{journey.correct === journey.total ? '¡Una ronda redonda!' : 'Un paso más, con nuevas pistas'}</h3>
          <p className="mt-3 text-4xl font-bold text-lime-300">{journey.correct} <span className="text-xl text-slate-400">/ {journey.total}</span></p>
          <p className="mt-2 text-slate-300">Respuestas correctas en esta ronda.</p>
          <p className="mt-4 text-sm text-slate-400">{journey.mistakes ? `${journey.mistakes} expresiones esperan un pequeño repaso.` : 'No quedan errores pendientes. Puedes seguir o volver cuando quieras.'}</p>
          <button className={`${primary} mt-6`} disabled={disabled} onClick={() => act(journey.mode === 'chapter' ? 'next' : 'resume')}>{journey.mode === 'chapter' ? 'Continuar mi camino →' : 'Volver a mi camino →'}</button>
        </div>}

        {finished && <div className="rounded-3xl bg-slate-900 p-7 text-center"><h3 className="text-2xl font-bold">{journey.final_unlocked ? 'Tu gran reto está listo' : 'Primero, refuerza las palabras difíciles'}</h3><p className="mt-3 text-slate-300">{journey.final_unlocked ? `Una pregunta por cada una de las ${journey.word_count} entradas del glosario. Todo se guarda, pregunta a pregunta.` : 'Has completado las mini lecciones. Repasa los errores para desbloquear el test de toda la unidad.'}</p>{journey.last_final && <p className="mt-4 font-bold text-lime-300">Último gran reto: {journey.last_final.correct} de {journey.last_final.total} respuestas correctas.</p>}{journey.final_unlocked && <button className={`${primary} mt-6`} disabled={disabled} onClick={() => act('final')}>{journey.last_final ? 'Volver a ponerme a prueba' : 'Empezar el gran reto →'}</button>}</div>}
      </div>

      {journey.mode === 'chapter' && !journey.feedback && <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-700 pt-5"><p className="text-sm text-slate-400">{journey.mistakes ? 'Un repaso breve te ayuda a recordar lo que antes costaba.' : 'El gran reto se abre al terminar los capítulos y repasar los errores.'}</p>{journey.mistakes > 0 && <button className={secondary} disabled={disabled} onClick={() => act('review')}>Repasar mis errores ({journey.mistakes})</button>}</div>}
      {error && <div role="alert" className="mt-4 rounded-xl bg-orange-300/10 p-4 text-orange-100"><p>{error}</p>{pending && <button className={`${secondary} mt-3`} disabled={busy} onClick={() => void send(pending)}>Reintentar el guardado</button>}</div>}
    </div>
  </section>
}
