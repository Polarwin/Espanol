import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { ConversationResult } from '../api/types'
import { IconMic, IconSpeaker } from '../components/icons'
import { useRecorder } from '../hooks/useRecorder'
import { useSpeechExample } from '../hooks/useSpeechExample'

function TutorMessage({ text }: { text: string }) {
  const speech = useSpeechExample(text)
  return <div className="flex items-start gap-3"><div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-sun-soft text-xl">👩🏽</div><div className="max-w-[85%] rounded-3xl rounded-tl-md bg-paper p-4 shadow-soft"><p className="font-semibold">{text}</p><button onClick={() => void speech.play()} disabled={speech.loading} className="mt-2 flex items-center gap-1.5 text-sm font-bold text-river disabled:opacity-50"><IconSpeaker size={16} />{speech.playing ? 'Reproduciendo…' : 'Escuchar'}</button></div></div>
}

export function Conversacion() {
  const { state, blob, seconds, start, stop, reset } = useRecorder()
  const [turn, setTurn] = useState(0)
  const [messages, setMessages] = useState<{ role: 'tutor' | 'user'; text: string }[]>([{ role: 'tutor', text: '¡Hola! Soy Ana, tu vecina. ¿Cómo estás hoy?' }])
  const [result, setResult] = useState<ConversationResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (state !== 'recorded' || !blob) return
    let cancelled = false
    setBusy(true); setError('')
    api.respondToConversation(turn, blob).then((response) => {
      if (cancelled) return
      setMessages((old) => [...old, { role: 'user', text: response.transcript }, { role: 'tutor', text: response.reply }])
      setResult(response); setTurn(response.turn); reset()
    }).catch(() => { if (!cancelled) setError('No pude entender el audio. Inténtalo otra vez.') }).finally(() => { if (!cancelled) setBusy(false) })
    return () => { cancelled = true }
  }, [state, blob, turn, reset])

  const restart = () => { setTurn(0); setResult(null); setMessages([{ role: 'tutor', text: '¡Hola! Soy Ana, tu vecina. ¿Cómo estás hoy?' }]); reset() }
  return <div className="mx-auto max-w-3xl px-4 py-5 sm:px-8 sm:py-8"><div className="rounded-3xl bg-[linear-gradient(135deg,#17324d,#24566f)] p-5 text-paper shadow-card sm:p-7"><p className="text-xs font-bold uppercase tracking-[.18em] text-sun">Conversación A1–A2</p><h1 className="mt-2 font-display text-3xl font-bold">Charla con una vecina</h1><p className="mt-2 text-paper/80">Responde con tus propias palabras. No necesitas repetir una frase exacta.</p></div>
    <div className="mt-5 space-y-4 rounded-3xl bg-cream p-4 sm:p-6">{messages.map((message, index) => message.role === 'tutor' ? <TutorMessage key={index} text={message.text} /> : <div key={index} className="flex justify-end"><div className="max-w-[85%] rounded-3xl rounded-tr-md bg-terracotta p-4 font-semibold text-paper">{message.text}</div></div>)}</div>
    {result && <div className="mt-4 rounded-2xl border border-leaf/20 bg-leaf-soft p-4"><p className="font-bold text-leaf">Consejo</p><p className="text-sm font-semibold">{result.feedback}</p>{!result.complete && <div className="mt-2 flex flex-wrap gap-2">{result.suggestions.map((s) => <span key={s} className="rounded-full bg-paper px-3 py-1 text-xs font-bold text-ink-soft">{s}</span>)}</div>}</div>}
    {error && <p className="mt-3 font-bold text-terracotta">{error}</p>}
    <div className="sticky bottom-16 mt-5 rounded-3xl bg-paper p-4 text-center shadow-card md:bottom-4">{result?.complete ? <button onClick={restart} className="rounded-full bg-terracotta px-6 py-3 font-bold text-paper">Empezar otra vez</button> : <button onClick={() => state === 'recording' ? stop() : void start()} disabled={busy} className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full text-paper shadow-card ${state === 'recording' ? 'animate-pulse bg-terracotta-dark' : 'bg-terracotta'}`}><IconMic size={28} /></button>}<p className="mt-2 text-sm font-bold text-ink-soft">{busy ? 'Ana está pensando…' : state === 'recording' ? `Grabando… ${seconds}s — toca para terminar` : result?.complete ? '¡Conversación completada!' : 'Toca y responde en español'}</p></div>
  </div>
}
