import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { PronunciationResult } from '../api/types'
import { useRecorder } from '../hooks/useRecorder'
import { IconCheck, IconMic } from './icons'
import { Waveform } from './Waveform'

interface RepeatPhraseCardProps {
  phraseId: string
  phrase: string
  tip?: string
}

/** "Repite la frase" card: mic button (MediaRecorder) + waveform + feedback. */
export function RepeatPhraseCard({ phraseId, phrase, tip }: RepeatPhraseCardProps) {
  const { state, error, blob, seconds, start, stop, reset } = useRecorder()
  const [evaluating, setEvaluating] = useState(false)
  const [result, setResult] = useState<PronunciationResult | null>(null)
  const [evaluationError, setEvaluationError] = useState('')

  // Evaluate with the backend as soon as a recording is available.
  useEffect(() => {
    if (state !== 'recorded' || !blob) return
    let cancelled = false
    setEvaluating(true)
    setEvaluationError('')
    api
      .evaluatePronunciation(phraseId, phrase, blob)
      .then((r) => {
        if (!cancelled) setResult(r)
      })
      .catch(() => {
        if (!cancelled) setEvaluationError('El análisis de pronunciación aún no está disponible. Puedes escuchar y repetir la frase.')
      })
      .finally(() => {
        if (!cancelled) setEvaluating(false)
      })
    return () => {
      cancelled = true
    }
  }, [state, blob, phraseId, phrase])

  const recording = state === 'recording'

  return (
    <div className="rounded-3xl bg-paper px-4 py-5 shadow-soft sm:px-6">
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:gap-6">
        <button
          onClick={() => {
            if (recording) stop()
            else {
              setResult(null)
              reset()
              void start()
            }
          }}
          aria-label={recording ? 'Detener grabación' : 'Grabar'}
          className={`flex h-16 w-16 shrink-0 items-center justify-center rounded-full text-paper shadow-card transition ${
            recording ? 'animate-pulse bg-terracotta-dark' : 'bg-terracotta hover:bg-terracotta-dark'
          }`}
        >
          <IconMic size={26} />
        </button>

        <div className="min-w-0 flex-1 text-center">
          <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-terracotta">Di en voz alta</p>
          <h2 className="mt-1 font-display text-2xl font-bold sm:text-[26px]">«{phrase}»</h2>
          {tip && <p className="mt-1 text-sm font-semibold text-river">Consejo: {tip}</p>}
          <div className="mt-2 flex justify-center">
            <Waveform
              bars={44}
              live={recording}
              progress={result ? 1 : 0}
              activeClass={result ? 'bg-leaf' : 'bg-terracotta'}
              idleClass={recording ? 'bg-terracotta/50' : 'bg-ink/15'}
              height={40}
            />
          </div>
          <p className="mt-2 text-sm font-semibold text-ink-soft">
            {recording
              ? `Grabando… ${seconds}s`
              : evaluating
                ? 'Escuchando tu pronunciación…'
                : result
                  ? `Puntuación: ${result.score}/100 — ${result.feedback}`
                  : (evaluationError || error || 'Habla cuando estés listo')}
          </p>
          {result && (
            <div className="mt-2 flex flex-wrap justify-center gap-1.5">
              {result.word_scores.map((w) => (
                <span
                  key={w.word}
                  className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-bold ${
                    w.score >= 75 ? 'bg-leaf-soft text-leaf' : 'bg-sun-soft text-terracotta-dark'
                  }`}
                >
                  {w.score >= 75 && <IconCheck size={11} />}
                  {w.word}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
      {recording && (
        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-navy-deep/90 p-5" role="dialog" aria-modal="true" aria-label="Grabando pronunciación">
          <div className="w-full max-w-lg rounded-3xl bg-paper p-6 text-center shadow-card sm:p-8">
            <p className="text-sm font-extrabold uppercase tracking-[0.18em] text-terracotta">Ahora dilo en español</p>
            <p className="mt-4 font-display text-3xl font-bold leading-snug sm:text-4xl">«{phrase}»</p>
            {tip && <p className="mt-3 font-semibold text-river">{tip}</p>}
            <div className="mt-6 flex justify-center"><Waveform bars={44} live height={48} activeClass="bg-terracotta" /></div>
            <p className="mt-3 font-bold text-ink-soft">Grabando… {seconds}s</p>
            <button onClick={stop} className="mt-6 w-full rounded-2xl bg-terracotta px-6 py-3.5 font-bold text-paper shadow-card sm:w-auto">Terminar grabación</button>
          </div>
        </div>
      )}
    </div>
  )
}
