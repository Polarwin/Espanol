import { useState } from 'react'
import { api } from '../api/client'
import type { ClipQuiz, ClipQuizResult } from '../api/types'

/**
 * Quick comprehension check shown after watching/listening to a clip:
 * pick the meaning of the line you just heard.
 */
export function ClipQuizCard({ quiz }: { quiz: ClipQuiz }) {
  const [selected, setSelected] = useState<string | null>(null)
  const [result, setResult] = useState<ClipQuizResult | null>(null)
  const [checking, setChecking] = useState(false)
  const [error, setError] = useState('')

  const check = async (choice: string) => {
    if (result || checking) return
    setSelected(choice)
    setChecking(true)
    setError('')
    try {
      setResult(await api.answerClipQuiz(choice))
    } catch {
      setError('No se pudo comprobar la respuesta. Inténtalo otra vez.')
      setSelected(null)
    } finally {
      setChecking(false)
    }
  }

  return (
    <section className="rounded-3xl bg-paper p-4 shadow-soft sm:p-5">
      <p className="text-xs font-extrabold uppercase tracking-wide text-river">Comprueba</p>
      <h3 className="mt-1 font-display text-lg font-bold">{quiz.prompt}</h3>
      <div className="mt-3 flex flex-col gap-2.5">
        {quiz.options.map((opt) => {
          const isSelected = selected === opt
          const isAnswer = result?.correct_answer === opt
          return (
            <button
              key={opt}
              type="button"
              disabled={Boolean(result) || checking}
              onClick={() => void check(opt)}
              className={`rounded-2xl border-2 px-4 py-3 text-left text-[15px] font-semibold transition ${
                result && isAnswer
                  ? 'border-leaf bg-leaf-soft text-leaf'
                  : result && isSelected && !result.correct
                    ? 'border-terracotta bg-blush text-terracotta'
                    : isSelected
                      ? 'border-river bg-river-soft'
                      : 'border-ink/10 hover:border-ink/25'
              }`}
            >
              {opt}
            </button>
          )
        })}
      </div>
      {result && (
        <p className={`mt-3 text-sm font-bold ${result.correct ? 'text-leaf' : 'text-terracotta'}`}>
          {result.correct ? '¡Correcto! Has entendido el clip.' : `No exactamente: la respuesta correcta es «${result.correct_answer}».`}
        </p>
      )}
      {error && <p className="mt-3 text-sm font-bold text-terracotta">{error}</p>}
    </section>
  )
}
