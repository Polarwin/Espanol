import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { AttemptResult, Exercise, TodayPath } from '../api/types'
import { IconChat, IconCheck } from '../components/icons'
import { Link } from 'react-router-dom'

export function Practica() {
  const [today, setToday] = useState<TodayPath | null>(null)
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<AttemptResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const path = await api.getTodayPath()
        const assessment = await api.getAssessment(path.lesson.id)
        if (cancelled) return
        setToday(path)
        setExercises(assessment.groups.flatMap((group) => group.exercises).slice(0, 5))
      } catch {
        if (!cancelled) setError('No se pudo preparar la práctica.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => { cancelled = true }
  }, [])

  const exercise = exercises[index]

  async function check() {
    if (!exercise || !answer.trim()) return
    setError('')
    try {
      setResult(await api.submitAttempt(exercise.id, answer.trim()))
    } catch {
      setError('No se pudo guardar la respuesta. Inténtalo otra vez.')
    }
  }

  function next() {
    if (index + 1 >= exercises.length) setDone(true)
    else setIndex((value) => value + 1)
    setAnswer('')
    setResult(null)
  }

  if (loading) return <div className="p-6 text-ink-soft">Preparando tu práctica…</div>
  if (error && !exercise) return <div className="p-6 font-semibold text-terracotta">{error}</div>

  return (
    <div className="mx-auto flex min-h-[calc(100vh-3.5rem)] max-w-2xl flex-col justify-center px-4 py-8 sm:px-8 md:min-h-screen">
      <div className="rounded-3xl bg-paper p-5 shadow-card sm:p-8">
        <Link to="/repaso" className="float-right rounded-full bg-sun-soft px-4 py-2 text-sm font-bold text-terracotta-dark">Repasar mis errores</Link>
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-blush text-terracotta">
          {done ? <IconCheck size={27} /> : <IconChat size={27} />}
        </span>
        {done ? (
          <>
            <h1 className="mt-5 font-display text-3xl font-bold">¡Práctica completada!</h1>
            <p className="mt-2 font-semibold text-ink-soft">Tus respuestas ya se reflejan en tu ruta adaptativa.</p>
            <button onClick={() => { setIndex(0); setDone(false) }} className="mt-6 w-full rounded-2xl bg-terracotta py-3 font-bold text-paper">Practicar otra vez</button>
          </>
        ) : exercise ? (
          <>
            <div className="mt-5 flex items-center justify-between gap-3">
              <div><h1 className="font-display text-2xl font-bold">Práctica rápida</h1><p className="text-sm font-semibold text-ink-soft">{today?.lesson.title}</p></div>
              <span className="rounded-full bg-river-soft px-3 py-1 text-sm font-bold text-river">{index + 1} de {exercises.length}</span>
            </div>
            <p className="mt-6 text-lg font-bold">{exercise.prompt}</p>
            {exercise.options ? (
              <div className="mt-4 grid gap-2">
                {exercise.options.map((option) => <button key={option} disabled={Boolean(result)} onClick={() => setAnswer(option)} className={`rounded-2xl border-2 px-4 py-3 text-left font-semibold ${answer === option ? 'border-river bg-river-soft' : 'border-ink/10'}`}>{option}</button>)}
              </div>
            ) : (
              <textarea rows={4} disabled={Boolean(result)} value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Escribe tu respuesta…" className="mt-4 w-full rounded-2xl border-2 border-ink/10 px-4 py-3 outline-none focus:border-river" />
            )}
            {result && <p className={`mt-4 font-bold ${result.correct ? 'text-leaf' : 'text-terracotta'}`}>{result.feedback}</p>}
            {error && <p className="mt-4 font-bold text-terracotta">{error}</p>}
            <button onClick={result ? next : () => void check()} disabled={!answer.trim()} className="mt-5 w-full rounded-2xl bg-terracotta py-3 font-bold text-paper disabled:opacity-40">{result ? (index + 1 === exercises.length ? 'Terminar' : 'Siguiente') : 'Comprobar'}</button>
          </>
        ) : <p className="mt-5 font-semibold text-ink-soft">No hay ejercicios disponibles.</p>}
      </div>
    </div>
  )
}
