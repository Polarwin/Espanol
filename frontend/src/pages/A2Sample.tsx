import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { A2Sample as Sample, A2StudyState, A2Correction } from '../api/types'
import { VocabularyJourney } from '../components/VocabularyJourney'
import { WritingFeedback } from '../components/WritingFeedback'
import { TextbookQuiz } from '../components/TextbookQuiz'

const button = 'rounded-xl bg-lime-300 px-4 py-2 font-bold text-slate-950 disabled:opacity-50'
const secondary = 'rounded-xl border border-slate-500 px-4 py-2 font-semibold text-white disabled:opacity-50'
const panel = 'rounded-3xl bg-slate-800 p-5 sm:p-7'

function TextbookAudio({ track }: { track: number }) {
  const [url, setUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const objectUrl = useRef('')
  useEffect(() => () => { if (objectUrl.current) URL.revokeObjectURL(objectUrl.current) }, [])
  async function load() {
    setBusy(true); setError('')
    try {
      const blob = await api.getA2Audio(track)
      if (objectUrl.current) URL.revokeObjectURL(objectUrl.current)
      objectUrl.current = URL.createObjectURL(blob)
      setUrl(objectUrl.current)
    } catch { setError('No se pudo cargar el audio. Inténtalo de nuevo.') }
    finally { setBusy(false) }
  }
  return <div className="my-3">
    {url ? <audio controls src={url} className="w-full" aria-label={`Audio del libro, pista ${track}`} />
      : <button className={secondary} disabled={busy} onClick={() => void load()}>{busy ? 'Cargando…' : `Escuchar pista ${track} del libro`}</button>}
    {error && <p role="alert">{error}</p>}
  </div>
}

export function A2Sample() {
  const [data, setData] = useState<Sample | null>(null)
  const [state, setState] = useState<A2StudyState>({ language: 'es', reviewed: [], draft: '', original: '' })
  const [error, setError] = useState('')
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [grammarText, setGrammarText] = useState('')
  const [grammarResult, setGrammarResult] = useState<A2Correction | null>(null)
  const [writingResult, setWritingResult] = useState<A2Correction | null>(null)
  const [reviewing, setReviewing] = useState<'grammar' | 'writing' | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')
  const [reviewError, setReviewError] = useState('')

  useEffect(() => {
    api.getA2Sample().then(result => { setData(result); setState(result.state) })
      .catch(() => setError('No se pudo cargar la muestra. Recarga la página para intentarlo de nuevo.'))
  }, [])

  function update(patch: Partial<A2StudyState>) {
    setState(current => ({ ...current, ...patch })); setSaveMessage('Cambios sin guardar')
  }
  async function save() {
    setSaving(true)
    try { await api.saveA2Sample(state); setSaveMessage('Guardado en tu cuenta') }
    catch { setSaveMessage('No se pudo guardar. Inténtalo de nuevo antes de salir.') }
    finally { setSaving(false) }
  }
  async function review(kind: 'grammar' | 'writing') {
    const text = kind === 'grammar' ? grammarText : state.draft
    setReviewing(kind); setReviewError('')
    try {
      const result = await api.correctA2Writing(text, kind)
      if (kind === 'grammar') setGrammarResult(result)
      else {
        setWritingResult(result)
        if (!state.original) update({ original: text })
      }
    } catch { setReviewError('No se pudo revisar. Tu texto sigue aquí; inténtalo de nuevo.') }
    finally { setReviewing(null) }
  }
  if (!data) return <p className="p-8" role="status">{error || 'Cargando A2 · Unidad 1…'}</p>
  return <main className="min-h-screen bg-slate-950 px-4 py-6 text-white sm:px-8">
    <div className="mx-auto max-w-4xl space-y-6">
      <header>
        <Link to="/lecciones" className="text-sm text-lime-300">← Todas las unidades</Link>
        <p className="mt-5 text-sm font-bold uppercase tracking-widest text-lime-300">Muestra · Vitamina A2 · Unidad 1</p>
        <h1 className="mt-2 text-3xl font-bold sm:text-5xl">Conocer y conocerse</h1>
        <p className="mt-3 max-w-2xl text-slate-300">Habla de tus gustos, encuentra intereses en común y explica qué te cuesta. Aprende las palabras del libro y úsalas al escuchar, conversar y escribir.</p>
        <p className="mt-2 text-sm text-slate-400">Libro: pp. 8–14 · Gramática: pp. 110–112 · Glosario: p. 148 · Transcripciones: p. 155</p>
        <nav aria-label="Pasos de la unidad" className="mt-4 flex flex-wrap gap-3 text-lime-300">
          <a href="#palabras">1. Vocabulario</a><a href="#gramatica">2. Gramática</a><a href="#escuchar">3. Escuchar</a><a href="#usar">4. Hablar y escribir</a>
        </nav>
      </header>
      <VocabularyJourney />
      <section id="gramatica" className={panel}>
        <h2 className="text-2xl font-bold">2. Entiende y practica la gramática</h2>
        <div className="my-4 grid gap-3 sm:grid-cols-2">
          <p><strong>Gustos:</strong> Me gusta leer. Me gustan los libros. El verbo cambia con la cosa que gusta.</p>
          <p><strong>Coincidir:</strong> Me gusta leer → A mí también. No me gusta correr → A mí tampoco.</p>
          <p><strong>Dificultad:</strong> Me cuesta hablar. Me cuestan las conversaciones rápidas.</p>
          <p><strong>Consejos:</strong> Puedes practicar. Te recomiendo escuchar. Hay que repetir. Usa el infinitivo.</p>
        </div>
        <p className="mb-4 text-sm text-slate-300">Elige una respuesta para ver la explicación.</p>
        <div className="space-y-4">{data.grammar.map((item, index) => <fieldset key={item.prompt} className="rounded-xl bg-slate-900 p-4">
          <legend className="px-1 font-semibold">{item.prompt.replace(` (${item.options.join(' / ')})`, '')}</legend>
          <div className="mt-2 grid grid-cols-2 gap-3">{item.options.map(option => {
            const selected = answers[index] === option
            const correct = option.toLocaleLowerCase('es') === item.answer
            const answered = answers[index] !== undefined
            return <button key={option} type="button" aria-pressed={selected} aria-describedby={answered ? `grammar-feedback-${index}` : undefined} onClick={() => setAnswers(current => ({ ...current, [index]: option }))} className={`min-h-12 rounded-xl border-2 px-4 py-3 text-lg font-bold transition ${answered && correct ? 'border-lime-300 bg-lime-300/10 text-lime-200' : selected ? 'border-orange-300 bg-orange-300/10 text-orange-100' : 'border-slate-600 bg-slate-800 hover:border-lime-300'}`}>
              {option}{answered && correct ? ' ✓' : selected ? ' ↻' : ''}
            </button>
          })}</div>
          {answers[index] !== undefined && <p id={`grammar-feedback-${index}`} className="mt-3 text-lime-200" role="status">{answers[index].toLocaleLowerCase('es') === item.answer ? 'Correcto. ' : `Respuesta: ${item.answer}. `}{item.rule}</p>}
        </fieldset>)}</div>
        <label htmlFor="grammar-writing" className="mt-5 block font-bold">Ahora crea tres frases: un gusto, una dificultad y un consejo.</label>
        <p className="mt-2 text-sm text-slate-300">Nota orientativa sobre 3: un punto por cada objetivo expresado con una idea comprensible. La corrección lingüística se muestra aparte; los espacios no restan puntos.</p>
        <textarea id="grammar-writing" disabled={reviewing === 'grammar'} className="mt-2 w-full rounded-xl bg-slate-900 p-3" rows={3} maxLength={2000} value={grammarText} onChange={e => { setGrammarText(e.target.value); setGrammarResult(null) }} placeholder="Me gustan… Me cuesta… Te recomiendo…" />
        <button className={button} disabled={!!reviewing || !grammarText.trim()} onClick={() => void review('grammar')}>{reviewing === 'grammar' ? 'Revisando…' : 'Revisar mis frases'}</button>
        {grammarResult && <>
          <div className="mt-4 rounded-xl bg-slate-900 p-4" role="status">
            {grammarResult.assessment?.status === 'graded' ? <>
              <h3 className="font-bold text-lime-200">Objetivos comunicativos: {grammarResult.assessment.score}/3</h3>
              {Object.entries(grammarResult.assessment.criteria ?? {}).map(([key, item]) => <div key={key} className="mt-3">
                <p className="font-semibold">{({ preference: 'Un gusto', difficulty: 'Una dificultad', advice: 'Un consejo' } as Record<string, string>)[key]}: {item.met ? '1/1 ✓' : '0/1 · Por completar'}</p>
                {item.evidence && <p className="text-slate-300">«{item.evidence}»</p>}<p>{item.feedback}</p>
              </div>)}
              <p className="mt-3 text-xs text-slate-300">Evaluación orientativa del modelo local. 3/3 significa que expresaste los tres objetivos, no que el texto esté libre de errores.</p>
            </> : <p>No se pudo calcular la nota. Inténtalo de nuevo; no cuenta como un cero.</p>}
          </div>
          <WritingFeedback correction={grammarResult} dark />
        </>}
      </section>
      <section id="escuchar" className={panel}>
        <h2 className="text-2xl font-bold">3. Escucha el libro</h2>
        <p className="mt-3">Pista 1 · ¿Cómo puedes encontrar personas con intereses en común? Escucha y busca qué aplicación reúne a personas para hacer deporte.</p>
        <TextbookAudio track={1} />
        <TextbookQuiz track={1} />
        <p className="mt-6">Pista 2 · ¿Qué le cuesta a Jake? ¿Qué actividad recomienda la profesora para mejorar su acento? ¿Y para conocer gente?</p>
        <TextbookAudio track={2} />
        <TextbookQuiz track={2} />
      </section>
      <section id="usar" className={panel}>
        <h2 className="text-2xl font-bold">4. Usa lo que has aprendido</h2>
        <p className="mt-3">Conversación: preséntate, compara tus gustos, explica una dificultad y pide una recomendación. Intenta usar tres expresiones del glosario.</p>
        {data.lesson_id && <div className="my-4 flex flex-wrap gap-3"><Link className={button} to={`/practica/conversacion/${data.lesson_id}`}>Practicar el diálogo</Link><Link className={secondary} to={`/leccion/${data.lesson_id}/repetir-video`}>Escuchar y repetir</Link></div>}
        <label htmlFor="unit-writing" className="mt-6 block font-bold">Escribe a un compañero nuevo (unas 60–80 palabras)</label>
        <p className="mt-2 text-slate-300">Describe tu personalidad, dos intereses, una dificultad y una actividad para practicar juntos. Añade una recomendación. Usa palabras del glosario y las estructuras de esta unidad.</p>
        <textarea id="unit-writing" className="mt-3 w-full rounded-xl bg-slate-900 p-3" rows={7} maxLength={2000} value={state.draft} onChange={e => { update({ draft: e.target.value }); setWritingResult(null) }} placeholder="Hola, soy… Me interesa… Me cuesta…" />
        <button className={button} disabled={!!reviewing || !state.draft.trim()} onClick={() => void review('writing')}>{reviewing === 'writing' ? 'Revisando…' : 'Revisar mi texto'}</button>
        {writingResult && <WritingFeedback correction={writingResult} dark />}
        {state.original && <details className="mt-4"><summary className="cursor-pointer text-lime-300">Comparar con mi primer borrador</summary><p className="mt-2 whitespace-pre-wrap">{state.original}</p></details>}
        <p className="mt-3 text-sm text-slate-300">Revisa las sugerencias y edita tu texto. Comprueba tú también si has incluido los gustos, la dificultad y la recomendación: la corrección no califica el contenido.</p>
      </section>
      {reviewError && <p role="alert" className="text-orange-200">{reviewError}</p>}
      <footer className="rounded-2xl border border-slate-600 bg-slate-900 p-4 shadow-xl">
        <button className={button} disabled={saving} onClick={() => void save()}>{saving ? 'Guardando…' : 'Guardar mi borrador'}</button>
        <p className="mt-2 text-sm text-slate-300" role="status">{saveMessage || 'El vocabulario se guarda automáticamente. Guarda tu borrador de escritura antes de salir.'}</p>
      </footer>
    </div>
  </main>
}
