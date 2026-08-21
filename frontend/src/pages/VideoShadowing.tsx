import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { LessonDetail, PronunciationResult } from '../api/types'
import { IconCheck, IconMic, IconPlay, IconReplay } from '../components/icons'
import { Waveform } from '../components/Waveform'
import { useRecorder } from '../hooks/useRecorder'

type Phase = 'listen' | 'playing' | 'repeat' | 'checking' | 'result'

export function VideoShadowing() {
  const { lessonId } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const fromRoute = searchParams.get('desde') === 'ruta'
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const { state, starting, error: recorderError, blob, seconds, start, stop, reset } = useRecorder()
  const [lesson, setLesson] = useState<LessonDetail | null>(null)
  const [index, setIndex] = useState(0)
  const [phase, setPhase] = useState<Phase>('listen')
  const [result, setResult] = useState<PronunciationResult | null>(null)
  const [error, setError] = useState('')
  const [finishing, setFinishing] = useState(false)

  useEffect(() => {
    if (!lessonId) return
    api.getLesson(Number(lessonId)).then(setLesson).catch(() => setError('No se pudo cargar el vídeo.'))
  }, [lessonId])

  const cues = useMemo(() => lesson?.segments.flatMap((segment) => {
    const lines = segment.transcript
    const span = Math.max(0.2, segment.end_seconds - segment.start_seconds)
    return lines.map((line, lineIndex) => ({
      id: `${segment.id}-${lineIndex}`,
      text: line.es,
      translation: line.en,
      start: segment.start_seconds + (lineIndex * span) / lines.length,
      end: segment.start_seconds + ((lineIndex + 1) * span) / lines.length,
    }))
  }) ?? [], [lesson])
  const cue = cues[index]

  useEffect(() => {
    if (state !== 'recorded' || !blob || !cue) return
    let cancelled = false
    setPhase('checking'); setError('')
    api.evaluatePronunciation(`shadow-${cue.id}`, cue.text, blob).then((value) => {
      if (!cancelled) { setResult(value); setPhase('result') }
    }).catch(() => {
      if (!cancelled) { setError('No pudimos analizar la pronunciación. Puedes grabarla otra vez.'); setPhase('repeat') }
    })
    return () => { cancelled = true }
  }, [state, blob, cue])

  const playCue = async (target: typeof cue) => {
    if (!videoRef.current || !target) return
    setResult(null); setError(''); reset(); setPhase('playing')
    videoRef.current.currentTime = target.start
    try { await videoRef.current.play() }
    catch { setError('Toca otra vez para reproducir esta frase.'); setPhase('listen') }
  }

  const playSentence = () => playCue(cue)

  const record = async () => {
    setResult(null); setError(''); reset()
    await start()
  }

  const next = async () => {
    if (index + 1 >= cues.length && fromRoute) {
      setFinishing(true); setError('')
      try { await api.advancePath('habla'); navigate('/ruta') }
      catch { setError('No se pudo guardar esta práctica. Inténtalo otra vez.'); setFinishing(false) }
      return
    }
    const nextIndex = index + 1 < cues.length ? index + 1 : 0
    setIndex(nextIndex)
    await playCue(cues[nextIndex])
  }

  if (!lesson) return <div className="p-6 font-semibold text-ink-soft">{error || 'Preparando el vídeo para repetir…'}</div>
  if (!cue) return <div className="p-6 font-semibold text-ink-soft">Esta lección no tiene frases para practicar todavía.</div>
  const recording = state === 'recording'

  return <div className="mx-auto max-w-4xl px-4 py-5 sm:px-8 sm:py-8">
    <p className="text-xs font-extrabold uppercase tracking-[.18em] text-terracotta">Escucha · pausa · repite</p>
    <h1 className="mt-2 font-display text-3xl font-bold">Repite el vídeo frase por frase</h1>
    <p className="mt-2 font-semibold text-ink-soft">{lesson.title} · Frase {index + 1} de {cues.length}</p>

    <section className="mt-5 overflow-hidden rounded-3xl bg-navy-deep shadow-card">
      <div className="relative aspect-video">
        <video
          ref={videoRef}
          src={lesson.video_url}
          playsInline
          className="h-full w-full object-cover"
          onTimeUpdate={(event) => {
            if (phase === 'playing' && event.currentTarget.currentTime >= cue.end - 0.04) {
              event.currentTarget.pause(); setPhase('repeat')
            }
          }}
          onEnded={() => setPhase('repeat')}
        />
        <div className="absolute inset-x-3 bottom-3 rounded-xl bg-black/75 px-4 py-3 text-center text-lg font-bold text-paper sm:inset-x-10 sm:bottom-5 sm:text-2xl">{cue.text}</div>
      </div>
    </section>

    <section className="mt-5 rounded-3xl bg-paper p-5 text-center shadow-soft sm:p-7">
      {phase === 'listen' && <><p className="font-display text-2xl font-bold">Primero, escucha la frase</p><button onClick={() => void playSentence()} className="mx-auto mt-5 flex items-center gap-2 rounded-full bg-river px-6 py-3 font-bold text-paper"><IconPlay size={19} />Escuchar en el vídeo</button></>}
      {phase === 'playing' && <><p className="font-display text-2xl font-bold">Escucha con atención…</p><div className="mt-4 flex justify-center"><Waveform bars={48} live activeClass="bg-river" /></div></>}
      {(phase === 'repeat' || recording) && <><p className="text-xs font-extrabold uppercase tracking-wider text-terracotta">Ahora tú</p><p className="mt-2 font-display text-2xl font-bold">«{cue.text}»</p><button onClick={recording ? stop : () => void record()} disabled={starting} className={`mx-auto mt-5 flex h-16 w-16 items-center justify-center rounded-full text-paper shadow-card disabled:opacity-50 ${recording ? 'animate-pulse bg-terracotta-dark' : 'bg-terracotta'}`} aria-label={recording ? 'Terminar grabación' : 'Grabar repetición'}><IconMic size={27} /></button><p className="mt-2 text-sm font-bold text-ink-soft">{recording ? `Grabando… ${seconds}s — toca para terminar` : 'Toca, repite la frase y vuelve a tocar'}</p></>}
      {phase === 'checking' && <><p className="font-display text-2xl font-bold">Escuchando tu pronunciación…</p><div className="mt-4 flex justify-center"><Waveform bars={48} live activeClass="bg-sun" /></div></>}
      {phase === 'result' && result && <><div className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full text-paper ${result.score >= 75 ? 'bg-leaf' : 'bg-sun'}`}><IconCheck size={28} /></div><p className="mt-3 font-display text-3xl font-bold">{result.score}/100</p><p className="mt-1 font-semibold text-ink-soft">{result.feedback}</p><div className="mt-4 flex flex-wrap justify-center gap-1.5">{result.word_scores.map((word, wordIndex) => <span key={`${word.word}-${wordIndex}`} className={`rounded-full px-2.5 py-1 text-xs font-bold ${word.score >= 75 ? 'bg-leaf-soft text-leaf' : 'bg-sun-soft text-terracotta-dark'}`}>{word.word} · {word.score}</span>)}</div><div className="mt-5 flex flex-col justify-center gap-2 sm:flex-row"><button onClick={() => { reset(); setResult(null); setPhase('repeat') }} className="flex items-center justify-center gap-2 rounded-full border-2 border-terracotta px-5 py-3 font-bold text-terracotta"><IconReplay size={17} />Repetir esta frase</button><button disabled={finishing} onClick={() => void next()} className="rounded-full bg-terracotta px-6 py-3 font-bold text-paper disabled:opacity-50">{finishing ? 'Guardando…' : index + 1 === cues.length ? (fromRoute ? 'Terminar y continuar mi ruta' : 'Escuchar de nuevo desde el principio') : 'Escuchar la frase siguiente'}</button></div></>}
      {(error || recorderError) && <p className="mt-4 font-bold text-terracotta" role="alert">{error || recorderError}</p>}
      <details className="mt-4"><summary className="cursor-pointer text-sm font-bold text-river">Ver traducción</summary><p className="mt-2 font-semibold text-ink-soft">{cue.translation}</p></details>
    </section>
    <div className="mt-5 text-center"><Link to={`/leccion/${lesson.id}`} className="text-sm font-bold text-river">Volver a la unidad</Link></div>
  </div>
}
