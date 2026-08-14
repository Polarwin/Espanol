import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { PronunciationResult } from '../api/types'
import { useRecorder } from '../hooks/useRecorder'
import { IconCheck, IconMic } from './icons'
import { Waveform } from './Waveform'

interface RepeatPhraseCardProps {
  phraseId: string
}

/** "Repite la frase" card: mic button (MediaRecorder) + waveform + feedback. */
export function RepeatPhraseCard({ phraseId }: RepeatPhraseCardProps) {
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
      .evaluatePronunciation(phraseId, blob)
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
  }, [state, blob, phraseId])

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
          <h2 className="font-display text-2xl font-bold sm:text-[26px]">Repite la frase</h2>
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
    </div>
  )
}
