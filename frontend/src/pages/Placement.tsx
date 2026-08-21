import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setPlacementComplete } from '../api/client'
import type { PlacementQuestion, PlacementResult } from '../api/types'
import { AudioPlayer } from '../components/AudioPlayer'
import { ThemeToggle } from '../theme'

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const START_LEVEL = 'A2'

const LABELS: Record<string, string> = {
  vocabulary: 'Vocabulario',
  grammar: 'Gramática',
  listening: 'Comprensión auditiva',
  reading: 'Comprensión lectora',
}

export function Placement() {
  const navigate = useNavigate()
  const [level, setLevel] = useState(START_LEVEL)
  const [questions, setQuestions] = useState<PlacementQuestion[]>([])
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [blockAnswers, setBlockAnswers] = useState<Record<string, string>>({})
  const [taken, setTaken] = useState<Record<string, boolean>>({})
  const [result, setResult] = useState<PlacementResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setQuestions([])
    setIndex(0)
    setBlockAnswers({})
    setError('')
    api.getPlacement(level).then(setQuestions).catch(() => setError('No se pudo cargar la prueba de nivel.'))
  }, [level])

  const question = questions[index]

  const finish = useCallback(async (allAnswers: Record<string, string>) => {
    setBusy(true)
    try {
      const value = await api.submitPlacement(allAnswers)
      setPlacementComplete(true)
      setResult(value)
    } catch {
      setError('No se pudo guardar el resultado. Inténtalo otra vez.')
    } finally {
      setBusy(false)
    }
  }, [])

  async function next(answer: string) {
    if (!question || busy) return
    const updatedBlock = { ...blockAnswers, [question.id]: answer }
    const updatedAll = { ...answers, [question.id]: answer }
    setBlockAnswers(updatedBlock)
    setAnswers(updatedAll)
    setError('')
    if (index < questions.length - 1) {
      setIndex((value) => value + 1)
      return
    }
    setBusy(true)
    try {
      const grade = await api.gradePlacement(level, updatedBlock)
      const nextTaken = { ...taken, [level]: grade.passed }
      setTaken(nextTaken)
      const step = grade.passed ? 1 : -1
      const nextLevel = LEVELS[LEVELS.indexOf(level) + step]
      if (!nextLevel || nextLevel in nextTaken) {
        await finish(updatedAll)
        return
      }
      setLevel(nextLevel)
    } catch {
      setError('No se pudo corregir este bloque. Inténtalo otra vez.')
    } finally {
      setBusy(false)
    }
  }

  async function skip() {
    setBusy(true)
    setError('')
    try {
      const value = await api.skipPlacement()
      setPlacementComplete(true)
      setResult(value)
    } catch {
      setError('No se pudo iniciar tu ruta. Inténtalo otra vez.')
    } finally {
      setBusy(false)
    }
  }

  if (result) {
    return (
      <main className="relative flex min-h-screen items-center justify-center bg-cream px-4 py-6">
        <div className="absolute right-4 top-4"><ThemeToggle compact /></div>
        <section className="w-full max-w-lg rounded-3xl bg-paper p-6 text-center shadow-card sm:p-8">
          <p className="text-sm font-bold uppercase tracking-wider text-river">Tu nivel</p>
          <h1 className="mt-2 font-display text-5xl font-bold text-terracotta">{result.overall_level}</h1>
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {Object.entries(result.skill_levels).map(([skill, skillLevel]) => (
              <span key={skill} className="rounded-full bg-river-soft px-3 py-1 text-sm font-bold text-river">
                {LABELS[skill] ?? skill}: {skillLevel}
              </span>
            ))}
          </div>
          <p className="mt-4 font-semibold text-ink-soft">Tu ruta ajustará cada habilidad por separado. Puedes repetir la prueba cuando quieras desde tu perfil.</p>
          <button onClick={() => navigate('/')} className="mt-6 w-full rounded-xl bg-terracotta px-7 py-3 font-bold text-paper sm:w-auto">Empezar mi ruta</button>
        </section>
      </main>
    )
  }

  if (!question) return <div className="min-h-screen bg-cream p-6 font-semibold text-ink-soft"><div className="absolute right-4 top-4"><ThemeToggle compact /></div>{error || (busy ? 'Corrigiendo…' : 'Preparando la prueba…')}</div>

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-cream px-4 py-6">
      <div className="absolute right-4 top-4"><ThemeToggle compact /></div>
      <section className="w-full max-w-2xl rounded-3xl bg-paper p-5 shadow-card sm:p-8">
        <div className="flex items-center justify-between text-sm font-bold text-ink-soft">
          <span>{LABELS[question.skill] ?? question.skill}</span>
          <span>Nivel {level} · {index + 1} de {questions.length}</span>
        </div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-ink/10"><div className="h-full bg-terracotta" style={{ width: `${((index + 1) / questions.length) * 100}%` }} /></div>
        {question.passage && (
          <div className="mt-6 rounded-2xl bg-cream p-4 text-left font-semibold leading-relaxed text-ink-soft">{question.passage}</div>
        )}
        {question.audio_url && (
          <div className="mt-6"><AudioPlayer src={question.audio_url} /></div>
        )}
        <h1 className="mt-6 font-display text-2xl font-bold">{question.prompt}</h1>
        <div className="mt-5 grid gap-3">{question.options.map((option) => <button key={option} disabled={busy} onClick={() => void next(option)} className="rounded-2xl border-2 border-ink/10 px-5 py-4 text-left font-semibold hover:border-river hover:bg-river-soft disabled:opacity-50">{option}</button>)}</div>
        {error && <p className="mt-4 font-bold text-terracotta">{error}</p>}
        <button disabled={busy} onClick={() => void skip()} className="mt-6 text-sm font-bold text-ink-soft underline disabled:opacity-50">Soy principiante: empezar en A1</button>
      </section>
    </main>
  )
}
