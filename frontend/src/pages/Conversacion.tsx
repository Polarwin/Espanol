import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { ConversationResult, ConversationSetup } from '../api/types'
import { IconMic, IconSpeaker } from '../components/icons'
import { useRecorder } from '../hooks/useRecorder'
import { useSpeechExample } from '../hooks/useSpeechExample'

function TutorMessage({ text }: { text: string }) {
  const speech = useSpeechExample(text)
  return <div className="flex items-start gap-3"><div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-sun-soft text-xl">👩🏽</div><div className="max-w-[85%] rounded-3xl rounded-tl-md bg-paper p-4 shadow-soft"><p className="font-semibold">{text}</p><button onClick={() => void speech.play()} disabled={speech.loading} className="mt-2 flex items-center gap-1.5 text-sm font-bold text-river disabled:opacity-50"><IconSpeaker size={16} />{speech.playing ? 'Reproduciendo…' : 'Escuchar'}</button></div></div>
}

export function Conversacion() {
  const { lessonId } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const fromRoute = searchParams.get('desde') === 'ruta'
  const { state, starting, blob, seconds, start, stop, reset } = useRecorder()
  const [turn, setTurn] = useState(0)
  const [messages, setMessages] = useState<{ role: 'tutor' | 'user'; text: string }[]>([])
  const [setup, setSetup] = useState<ConversationSetup | null>(null)
  const [result, setResult] = useState<ConversationResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [routeBusy, setRouteBusy] = useState(false)
  const [error, setError] = useState('')

  async function continueRoute() {
    setRouteBusy(true)
    try {
      await api.advancePath('conversa')
    } catch {
      // The route may already have moved on; either way we return to it.
    } finally {
      navigate('/ruta')
    }
  }

  useEffect(() => {
    let cancelled = false
    api.getConversationSetup(lessonId).then((data) => {
      if (cancelled) return
      setSetup(data)
      setTurn(0); setResult(null); setMessages([{ role: 'tutor', text: data.greeting }]); reset()
    }).catch(() => { if (!cancelled) setError('No se pudo preparar esta conversación.') })
    return () => { cancelled = true }
  }, [lessonId, reset])

  useEffect(() => {
    if (state !== 'recorded' || !blob) return
    let cancelled = false
    setBusy(true); setError('')
    api.respondToConversation(turn, blob, setup?.lesson_id).then((response) => {
      if (cancelled) return
      setMessages((old) => [...old, { role: 'user', text: response.transcript }, { role: 'tutor', text: response.reply }])
      setResult(response); setTurn(response.turn); reset()
    }).catch(() => { if (!cancelled) setError('No pude entender el audio. Inténtalo otra vez.') }).finally(() => { if (!cancelled) setBusy(false) })
    return () => { cancelled = true }
  }, [state, blob, turn, reset, setup?.lesson_id])

  const restart = () => { if (!setup) return; setTurn(0); setResult(null); setMessages([{ role: 'tutor', text: setup.greeting }]); reset() }
  return <div className="mx-auto max-w-3xl px-4 py-5 sm:px-8 sm:py-8"><div className="rounded-3xl bg-[linear-gradient(135deg,#17324d,#24566f)] p-5 text-paper shadow-card sm:p-7"><p className="text-xs font-bold uppercase tracking-[.18em] text-sun">Conversación {setup?.cefr_level ?? ''} · {setup?.title ?? ''}</p><h1 className="mt-2 font-display text-3xl font-bold">{setup?.scene ?? 'Preparando conversación…'}</h1><p className="mt-2 text-paper/80">{setup?.goal ?? 'Responde con tus propias palabras.'}</p>{setup && <div className="mt-3 flex flex-wrap gap-2">{setup.vocabulary.map((word) => <span key={word} className="rounded-full bg-paper/12 px-3 py-1 text-xs font-bold">{word}</span>)}</div>}</div>
    <div className="mt-5 space-y-4 rounded-3xl bg-cream p-4 sm:p-6">{messages.map((message, index) => message.role === 'tutor' ? <TutorMessage key={index} text={message.text} /> : <div key={index} className="flex justify-end"><div className="max-w-[85%] rounded-3xl rounded-tr-md bg-terracotta p-4 font-semibold text-paper">{message.text}</div></div>)}</div>
    {result && <div className={`mt-4 rounded-2xl border p-4 ${result.correction.has_error ? 'border-terracotta/30 bg-terracotta/10' : 'border-leaf/20 bg-leaf-soft'}`}>
      <p className={`font-bold ${result.correction.has_error ? 'text-terracotta-dark' : 'text-leaf'}`}>{result.correction.has_error ? 'Vamos a corregirlo' : '¡Bien dicho!'}</p>
      {result.correction.has_error && <div className="mt-2 space-y-2 text-sm"><p><span className="font-extrabold text-ink-soft">Has dicho:</span> <span className="line-through decoration-terracotta">{result.correction.original}</span></p><p><span className="font-extrabold text-leaf">Mejor:</span> <span className="font-bold">{result.correction.corrected}</span></p><p className="font-semibold text-ink-soft">{result.correction.explanation}</p><TutorMessage text={result.correction.corrected} /></div>}
      {!result.correction.has_error && <p className="text-sm font-semibold">{result.correction.explanation}</p>}
      <p className="mt-2 text-sm font-semibold">{result.feedback}</p>{!result.complete && <div className="mt-2 flex flex-wrap gap-2">{result.suggestions.map((s) => <span key={s} className="rounded-full bg-paper px-3 py-1 text-xs font-bold text-ink-soft">{s}</span>)}</div>}
    </div>}
    {error && <p className="mt-3 font-bold text-terracotta">{error}</p>}
    <div className="sticky bottom-16 mt-5 rounded-3xl bg-paper p-4 text-center shadow-card md:bottom-4">{result?.complete ? <div className="flex flex-col items-center gap-2 sm:flex-row sm:justify-center">{fromRoute && <button onClick={() => void continueRoute()} disabled={routeBusy} className="rounded-full bg-terracotta px-6 py-3 font-bold text-paper disabled:opacity-50">{routeBusy ? 'Guardando…' : 'Continuar mi ruta'}</button>}<button onClick={restart} className={`rounded-full px-6 py-3 font-bold ${fromRoute ? 'bg-cream text-ink' : 'bg-terracotta text-paper'}`}>Empezar otra vez</button></div> : <button onClick={() => state === 'recording' ? stop() : void start()} disabled={busy || starting || !setup} aria-label={state === 'recording' ? 'Detener grabación' : 'Grabar respuesta'} className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full text-paper shadow-card disabled:opacity-50 ${state === 'recording' ? 'animate-pulse bg-terracotta-dark' : 'bg-terracotta'}`}><IconMic size={28} /></button>}<p className="mt-2 text-sm font-bold text-ink-soft">{busy ? 'Ana está pensando…' : state === 'recording' ? `Grabando… ${seconds}s — toca para terminar` : result?.complete ? '¡Conversación completada!' : 'Toca y responde en español'}</p>{setup && <Link to={`/leccion/${setup.lesson_id}`} className="mt-2 inline-block text-xs font-extrabold text-river">Volver a la unidad</Link>}</div>
  </div>
}
