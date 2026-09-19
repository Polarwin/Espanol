import { useEffect, useRef, useState } from 'react'

const questions = {
  1: [
    { prompt: '¿Qué aplicación conecta a personas para practicar deporte?', options: ['Meetup', 'Timpik', 'Una aplicación de traducción'], answer: 1, explanation: 'Timpik reúne a personas para hacer deporte.' },
    { prompt: '¿Qué reúne Meetup?', options: ['Grupos con intereses comunes', 'Solo profesores de idiomas', 'Solo deportistas profesionales'], answer: 0, explanation: 'Meetup permite encontrar grupos con intereses en común.' },
    { prompt: '¿Cuál es la idea principal?', options: ['Estudiar siempre a solas', 'Comprar material deportivo', 'Conocer gente a través de intereses compartidos'], answer: 2, explanation: 'Compartir intereses ayuda a conocer a otras personas.' },
  ],
  2: [
    { prompt: '¿Qué le cuesta a Jake?', options: ['Cocinar y comprar', 'Hablar y entender a la gente', 'Encontrar la biblioteca'], answer: 1, explanation: 'Jake tiene dificultades para hablar y entender a la gente.' },
    { prompt: '¿Qué recomienda la profesora para mejorar su acento?', options: ['Un taller de escritura', 'Leer noticias a solas', 'El taller de pronunciación'], answer: 2, explanation: 'El taller de pronunciación le ayuda a mejorar su acento.' },
    { prompt: '¿Dónde puede conocer gente y conversar?', options: ['En el café con Maca', 'En una tienda de deportes', 'En casa, sin hablar con nadie'], answer: 0, explanation: 'La profesora recomienda el café con Maca para conocer gente y conversar.' },
  ],
}

export function TextbookQuiz({ track }: { track: 1 | 2 }) {
  const all = questions[track]
  const [queue, setQueue] = useState<number[]>([])
  const [index, setIndex] = useState(0)
  const [selected, setSelected] = useState<number | null>(null)
  const [mistakes, setMistakes] = useState<number[]>([])
  const [score, setScore] = useState(0)
  const [started, setStarted] = useState(false)
  const [retry, setRetry] = useState(false)
  const locked = useRef(false)
  const question = all[queue[index]]
  const correct = question && selected === question.answer
  function next() { setIndex(i => i + 1); setSelected(null); locked.current = false }
  useEffect(() => {
    if (!correct) return
    const timer = window.setTimeout(() => { setIndex(i => i + 1); setSelected(null); locked.current = false }, 1400)
    return () => window.clearTimeout(timer)
  }, [correct, index])
  function start(ids: number[], review: boolean) {
    setQueue(ids); setIndex(0); setSelected(null); setMistakes([]); setScore(0); setStarted(true); setRetry(review); locked.current = false
  }
  const button = 'rounded-xl border border-slate-500 px-4 py-3 text-left font-semibold disabled:opacity-70'
  if (!started) return <button className={button} onClick={() => start(all.map((_, i) => i), false)}>Ya he escuchado · Empezar 3 preguntas</button>
  if (!question) return <div className="my-4 space-y-3" role="status">
    <p className="font-bold">{retry ? 'Repaso' : 'Resultado'}: {score}/{queue.length}</p>
    <p>{mistakes.length ? 'Vuelve a escuchar y practica las preguntas que te costaron.' : 'Has comprendido estas ideas del audio.'}</p>
    {mistakes.length > 0 && <button className={button} onClick={() => start(mistakes, true)}>Repasar mis errores ({mistakes.length})</button>}
    <button className={`${button} ml-2`} onClick={() => start(all.map((_, i) => i), false)}>Repetir las 3 preguntas</button>
  </div>
  return <fieldset className="my-4 rounded-xl bg-slate-900 p-4">
    <legend className="px-1">{retry ? 'Repaso' : 'Pregunta'} {index + 1}/{queue.length} · Pista {track}</legend>
    <p className="font-bold">{question.prompt}</p>
    <div className="mt-3 grid gap-2">{question.options.map((option, i) => <button key={option} className={`${button} ${selected !== null && i === question.answer ? 'border-lime-300 text-lime-200' : selected === i ? 'border-orange-300 text-orange-200' : ''}`} disabled={selected !== null} aria-pressed={selected === i} onClick={() => {
      if (locked.current) return
      locked.current = true; setSelected(i)
      if (i === question.answer) setScore(s => s + 1)
      else setMistakes(m => [...m, queue[index]])
    }}>{option}</button>)}</div>
    {selected !== null && <div className="mt-3" role="status"><p>{correct ? ['¡Bien escuchado!', '¡Exacto!', '¡Lo has entendido!'][queue[index] % 3] : 'Escucha otra vez si lo necesitas.'} {question.explanation}</p>
      {!correct && <button className={`${button} mt-3`} onClick={next}>Siguiente pregunta</button>}</div>}
  </fieldset>
}
