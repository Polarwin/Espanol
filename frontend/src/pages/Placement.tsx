import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setPlacementComplete } from '../api/client'
import type { PlacementQuestion, PlacementResult } from '../api/types'
import { ThemeToggle } from '../theme'

const LABELS: Record<string, string> = {
  vocabulary: 'Vocabulario',
  grammar: 'Gramática',
  listening: 'Comprensión',
}

export function Placement() {
  const navigate = useNavigate()
  const [questions, setQuestions] = useState<PlacementQuestion[]>([])
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<PlacementResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getPlacement().then(setQuestions).catch(() => setError('No se pudo cargar la prueba de nivel.'))
  }, [])

  const question = questions[index]

  async function next(answer: string) {
    if (!question || busy) return
    const updated = { ...answers, [question.id]: answer }
    setAnswers(updated)
    setError('')
    if (index < questions.length - 1) {
      setIndex((value) => value + 1)
      return
    }
    setBusy(true)
    try {
      const value = await api.submitPlacement(updated)
      setPlacementComplete(true)
      setResult(value)
    } catch {
      setError('No se pudo guardar el resultado. Inténtalo otra vez.')
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
          <p className="text-sm font-bold uppercase tracking-wider text-river">Tu punto de partida</p>
          <h1 className="mt-2 font-display text-5xl font-bold text-terracotta">{result.overall_level}</h1>
          <p className="mt-3 font-semibold text-ink-soft">Tu ruta ajustará cada habilidad por separado. Puedes cambiar de nivel rápidamente según tus resultados.</p>
          <button onClick={() => navigate('/')} className="mt-6 w-full rounded-xl bg-terracotta px-7 py-3 font-bold text-paper sm:w-auto">Empezar mi ruta</button>
        </section>
      </main>
    )
  }

  if (!question) return <div className="min-h-screen bg-cream p-6 font-semibold text-ink-soft"><div className="absolute right-4 top-4"><ThemeToggle compact /></div>{error || 'Preparando la prueba…'}</div>

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-cream px-4 py-6">
      <div className="absolute right-4 top-4"><ThemeToggle compact /></div>
      <section className="w-full max-w-2xl rounded-3xl bg-paper p-5 shadow-card sm:p-8">
        <div className="flex items-center justify-between text-sm font-bold text-ink-soft"><span>{LABELS[question.skill] ?? question.skill}</span><span>{index + 1} de {questions.length}</span></div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-ink/10"><div className="h-full bg-terracotta" style={{ width: `${((index + 1) / questions.length) * 100}%` }} /></div>
        <h1 className="mt-8 font-display text-2xl font-bold">{question.prompt}</h1>
        <div className="mt-5 grid gap-3">{question.options.map((option) => <button key={option} disabled={busy} onClick={() => void next(option)} className="rounded-2xl border-2 border-ink/10 px-5 py-4 text-left font-semibold hover:border-river hover:bg-river-soft disabled:opacity-50">{option}</button>)}</div>
        {error && <p className="mt-4 font-bold text-terracotta">{error}</p>}
        <button disabled={busy} onClick={() => void skip()} className="mt-6 text-sm font-bold text-ink-soft underline disabled:opacity-50">Soy principiante: empezar en A1</button>
      </section>
    </main>
  )
}
