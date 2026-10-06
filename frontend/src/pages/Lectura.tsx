import { useEffect, useRef, useState } from 'react'
import { api, ApiError } from '../api/client'
import type { ReadingJob } from '../api/client'

const button = 'rounded-xl bg-terracotta px-4 py-3 font-bold text-paper disabled:opacity-50'
const secondary = 'rounded-xl border border-ink-soft/20 px-4 py-2 font-bold hover:bg-cream'
const pending = (job: ReadingJob | null) => job?.status === 'queued' || job?.status === 'running'
const errorMessage = (error: unknown) => error instanceof ApiError && error.status === 409
  ? 'El generador está ocupado. Inténtalo en unos minutos.'
  : error instanceof ApiError && error.status === 422
    ? 'No hay textos o subtítulos utilizables en esa fuente. Prueba otra.'
    : 'No se pudo conectar con el servicio. Inténtalo de nuevo.'

export function Lectura() {
  const [history, setHistory] = useState<ReadingJob[]>([])
  const [job, setJob] = useState<ReadingJob | null>(null)
  const [source, setSource] = useState('auto')
  const [level, setLevel] = useState('A2')
  const [view, setView] = useState<'exercise' | 'translation' | 'answers'>('exercise')
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [dirty, setDirty] = useState(false)
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const selection = useRef(0)
  const jobId = job?.id
  const jobStatus = job?.status
  const [listening, setListening] = useState(true)
  const [revealed, setRevealed] = useState(false)
  const [audioUrl, setAudioUrl] = useState('')
  const [audioBusy, setAudioBusy] = useState(false)
  const [audioError, setAudioError] = useState('')
  const audioRequest = useRef<AbortController | null>(null)
  const audioElement = useRef<HTMLAudioElement | null>(null)
  const [speed, setSpeed] = useState('1')
  const showText = !listening || revealed

  useEffect(() => {
    audioRequest.current?.abort()
    setAudioUrl(''); setAudioError(''); setAudioBusy(false); setRevealed(false); setView('exercise')
    return () => { audioRequest.current?.abort() }
  }, [jobId])
  useEffect(() => () => { if (audioUrl) URL.revokeObjectURL(audioUrl) }, [audioUrl])

  async function loadAudio() {
    if (!job) return
    audioRequest.current?.abort()
    const controller = new AbortController()
    audioRequest.current = controller
    setAudioBusy(true); setAudioError('')
    try {
      const blob = await api.readingAudio(job.id, controller.signal)
      if (!controller.signal.aborted) setAudioUrl(URL.createObjectURL(blob))
    } catch (e) {
      if (!controller.signal.aborted) setAudioError(e instanceof ApiError && e.status === 404
        ? 'Este audio ya no está disponible. Puedes practicar con otra lectura o cambiar a modo lectura.'
        : e instanceof ApiError && e.status === 409 ? 'El generador está ocupado. Reintenta en unos minutos.'
          : 'No se pudo cargar el audio. Puedes reintentarlo.')
    } finally { if (!controller.signal.aborted) setAudioBusy(false) }
  }

  function accept(next: ReadingJob) {
    setJob(next); setAnswers(next.answers ?? {}); setDirty(false); setSaved(false); setView('exercise')
    setHistory(items => [next, ...items.filter(item => item.id !== next.id)].slice(0, 30))
  }
  useEffect(() => {
    let cancelled = false
    api.readingHistory().then(async items => {
      if (cancelled) return
      setHistory(items)
      if (items.length && selection.current === 0) {
        const next = await api.readingGet(items[0].id)
        if (!cancelled && selection.current === 0) accept(next)
      }
    }).catch(e => { if (!cancelled) setError(errorMessage(e)) })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    if (!jobId || (jobStatus !== 'queued' && jobStatus !== 'running')) return
    let stopped = false
    let timer: ReturnType<typeof setTimeout>
    const poll = async () => {
      try {
        const next = await api.readingGet(jobId)
        if (stopped) return
        setJob(next)
        setHistory(items => items.map(item => item.id === next.id ? next : item))
        setError('')
        if (pending(next)) timer = setTimeout(poll, 4000)
      } catch (e) {
        if (!stopped) { setError(errorMessage(e)); timer = setTimeout(poll, 8000) }
      }
    }
    timer = setTimeout(poll, 2000)
    return () => { stopped = true; clearTimeout(timer) }
  }, [jobId, jobStatus])

  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => { if (dirty) { event.preventDefault(); event.returnValue = '' } }
    window.addEventListener('beforeunload', warn)
    return () => window.removeEventListener('beforeunload', warn)
  }, [dirty])

  async function choose(id?: string) {
    if (dirty && !window.confirm('Tienes respuestas sin guardar. ¿Quieres continuar?')) return
    const request = ++selection.current
    setBusy(true); setError('')
    try {
      const next = id ? await api.readingGet(id) : await api.readingCreate(source, level)
      if (selection.current === request) accept(next)
    } catch (e) { setError(errorMessage(e)) }
    finally { setBusy(false) }
  }
  async function save() {
    if (!job) return
    setBusy(true); setError('')
    try { await api.readingSave(job.id, answers); setDirty(false); setSaved(true) }
    catch (e) { setError(errorMessage(e)) }
    finally { setBusy(false) }
  }
  const pack = job?.pack
  return <main className="mx-auto max-w-3xl space-y-6 px-4 py-6 sm:px-8">
    <section className="rounded-3xl bg-paper p-5 shadow-soft">
      <h2 className="font-display text-2xl font-bold">Lectura sorpresa</h2>
      <p className="mt-2 text-ink-soft">Escucha primero o lee: descubre un texto de tu biblioteca o de las noticias.</p>
      <div className="my-4 flex flex-wrap gap-4">
        <label className="text-sm font-bold">Nivel<select className="mt-1 block rounded-lg border p-2" value={level} onChange={e => setLevel(e.target.value)}>
          {['A1', 'A2', 'B1', 'B2', 'C1', 'C2'].map(x => <option key={x}>{x}</option>)}
        </select></label>
        <label className="text-sm font-bold">Fuente<select className="mt-1 block max-w-full rounded-lg border p-2" value={source} onChange={e => setSource(e.target.value)}>
          <option value="auto">Sorpréndeme · todas</option><option value="library">Biblioteca y libros</option><option value="news">NoticiasEspanol</option>
        </select></label>
      </div>
      <button className={button} disabled={busy || pending(job)} onClick={() => void choose()}>Crear una lectura sorpresa</button>
      <p className="mt-3 text-xs text-ink-soft">Modelo local · Puede tardar varios minutos. Puedes salir y volver: la generación continúa en el servidor. Necesitas conexión para generar y guardar.</p>
    </section>
    {error && <p role="alert" className="rounded-xl bg-paper p-4 text-terracotta">{error}</p>}
    {pending(job) && <section role="status" aria-live="polite" className="rounded-2xl bg-paper p-5">
      <h2 className="font-bold">{job?.stage}…</h2><p className="mt-2 break-words text-sm">{job?.source_title}</p>
      <p className="mt-2 text-sm text-ink-soft">Primero la lectura, después la traducción, las preguntas y el vocabulario.</p>
    </section>}
    {job?.status === 'failed' && <p role="alert" className="rounded-xl bg-paper p-4">{job.error} Usa «Crear una lectura sorpresa» para reintentar.</p>}
    {job?.status === 'ready' && pack && <article className="space-y-5 rounded-3xl bg-paper p-5 shadow-soft sm:p-7">
      <div><p className="text-sm font-bold text-terracotta">{job.level} · {job.source === 'news' ? 'Noticias' : 'Biblioteca'}</p>
        <h2 className="mt-1 font-display text-2xl font-bold">{pack.title}</h2>
        <p className="mt-3 rounded-xl bg-cream p-3 text-sm">Borrador de IA local, pendiente de revisión. Puede contener errores. Las noticias no están verificadas ni necesariamente son actuales. Sin calificación automática.</p>
      </div>
      <div aria-label="Modo de práctica" className="flex flex-wrap gap-2">
        <button className={listening ? button : secondary} aria-pressed={listening} onClick={() => { setListening(true); setRevealed(false); setView('exercise') }}>Escuchar primero</button>
        <button className={!listening ? button : secondary} aria-pressed={!listening} onClick={() => { setListening(false); setView('exercise') }}>Leer</button>
      </div>
      <section className="space-y-3 rounded-2xl bg-cream p-4" aria-label="Audio de la lectura">
        <h3 className="font-bold">{listening ? '1. Escucha sin mirar el texto' : 'Escucha la lectura'}</h3>
        <p className="text-sm">{job.pack?.audio_kind === 'original' ? 'Audio original del vídeo. Transcripción basada en sus subtítulos.' : 'Voz sintética en español.'} Repite las veces que necesites; después responde a las preguntas. Sin nota automática.</p>
        {!audioUrl && <button className={button} disabled={audioBusy} onClick={() => void loadAudio()}>{audioBusy ? 'Preparando audio…' : 'Cargar audio'}</button>}
        {audioBusy && <p role="status" className="text-sm">Preparando la narración local. Puede tardar unos segundos.</p>}
        {audioError && <p role="alert">{audioError}</p>}
        {audioUrl && <>
          <audio ref={audioElement} className="w-full" controls preload="metadata" src={audioUrl} aria-label="Narración en español"
            onLoadedMetadata={() => { if (audioElement.current) audioElement.current.playbackRate = Number(speed) }}
            onError={() => { setAudioError('No se pudo reproducir el audio. Vuelve a cargarlo.'); setAudioUrl('') }} />
          <div className="flex flex-wrap items-center gap-3">
            <button className={secondary} onClick={() => { if (audioElement.current) { audioElement.current.currentTime = 0; void audioElement.current.play().catch(() => setAudioError('Pulsa reproducir para escuchar.')) } }}>Escuchar otra vez</button>
            <label className="text-sm">Velocidad <select aria-label="Velocidad del audio" className="rounded-lg border p-2" value={speed} onChange={e => {
              setSpeed(e.target.value); if (audioElement.current) audioElement.current.playbackRate = Number(e.target.value)
            }}>{['0.75', '1', '1.25'].map(x => <option key={x} value={x}>{x}×</option>)}</select></label>
          </div>
        </>}
      </section>
      {showText && <nav aria-label="Páginas de la lectura" className="flex flex-wrap gap-2">
        {([['exercise', 'Lectura y preguntas'], ['translation', 'English translation'], ['answers', 'Respuestas orientativas']] as const).map(([key, label]) =>
          <button key={key} className={view === key ? button : secondary} aria-current={view === key ? 'page' : undefined} onClick={() => setView(key)}>{label}</button>)}
      </nav>}
      {view === 'exercise' && <>
        {showText && <div className="space-y-4 text-lg leading-relaxed">{pack.reading.split('\n').filter(Boolean).map((p, i) => <p key={i}>{p}</p>)}</div>}
        <h3 className="text-xl font-bold">{listening ? '2. ¿Qué has entendido?' : '¿Qué has entendido?'}</h3><p>Responde con tus propias palabras. Guarda tus respuestas antes de salir.</p>
        {pack.questions.map((q, i) => <label key={i} className="block font-semibold">{i + 1}. {q.question}
          <textarea disabled={busy} value={answers[String(i)] ?? ''} maxLength={4000} rows={3} className="mt-2 w-full rounded-xl border border-ink-soft/30 p-3 font-normal" onChange={e => {
            setAnswers(old => ({ ...old, [String(i)]: e.target.value })); setDirty(true); setSaved(false)
          }} />
        </label>)}
        <div className="flex items-center gap-3"><button disabled={busy || !dirty} className={button} onClick={() => void save()}>Guardar mis respuestas</button><span role="status">{saved ? 'Guardadas' : dirty ? 'Sin guardar' : ''}</span></div>
        {!showText && <div className="space-y-2 rounded-xl bg-cream p-4"><h3 className="font-bold">3. Comprueba lo que has entendido</h3>
          <p className="text-sm">Cuando estés listo, revela el texto, el vocabulario y las ayudas. Tus respuestas se conservan.</p>
          <button className={secondary} onClick={() => setRevealed(true)}>Mostrar transcripción y ayudas</button></div>}
        {showText && <><h3 className="text-xl font-bold">Palabras para llevarte</h3>
        <div className="grid gap-3 sm:grid-cols-2">{pack.vocabulary.map(word => <section key={word.term} className="rounded-2xl bg-cream p-4">
          <h4 className="text-lg font-bold">{word.term}</h4><p className="mt-2">{word.spanish}</p>
          <details className="mt-2 text-sm text-ink-soft"><summary className="cursor-pointer">English explanation</summary><p lang="en" className="mt-2">{word.english}</p></details>
        </section>)}</div>
        <button className={secondary} onClick={() => setView('translation')}>Siguiente página: English translation →</button></>}
      </>}
      {view === 'translation' && <section lang="en" className="space-y-4 text-lg leading-relaxed"><h3 className="font-bold">English translation</h3>{pack.translation.split('\n').filter(Boolean).map((p, i) => <p key={i}>{p}</p>)}
        <button className={secondary} onClick={() => setView('answers')}>Respuestas orientativas →</button></section>}
      {view === 'answers' && <section className="space-y-4"><h3 className="text-xl font-bold">Respuestas orientativas</h3><p>Compara las ideas, no las palabras exactas. Otras respuestas también pueden ser válidas.</p>
        {pack.questions.map((q, i) => <div key={i} className="rounded-xl bg-cream p-4"><h4 className="font-bold">{i + 1}. {q.question}</h4>
          <p className="mt-2 whitespace-pre-wrap">Tu respuesta: {answers[String(i)] || 'Todavía no has respondido.'}</p><p className="mt-2">Ejemplo: {q.suggested_answer}</p></div>)}
      </section>}
      <p className="break-words text-xs text-ink-soft">Fuente: {job.source_title}{pack.duration > 0 ? ` · Fragmento ${pack.start}–${pack.start + pack.duration} s` : ''}</p>
    </article>}
    {history.length > 0 && <section><h2 className="mb-3 text-xl font-bold">Tus lecturas guardadas</h2><div className="space-y-2">{history.map(item =>
      <button disabled={busy} key={item.id} onClick={() => void choose(item.id)} className="block w-full rounded-xl bg-paper p-4 text-left shadow-soft">
        <span className="block break-words font-bold">{item.source_title}</span><span className="text-sm text-ink-soft">{item.level} · {item.status === 'ready' ? 'Lista' : item.status === 'failed' ? 'No completada' : item.stage}</span>
      </button>)}</div></section>}
  </main>
}
