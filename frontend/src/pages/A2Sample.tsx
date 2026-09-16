import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { A2Sample as Sample, A2StudyState, A2Correction } from '../api/types'

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

function WritingFeedback({ result }: { result: A2Correction }) {
  return <div className="mt-3 space-y-2 rounded-xl bg-slate-900 p-4" aria-live="polite">
    <p className="font-bold">{result.status === 'unavailable' ? 'La revisión no está disponible. Conserva tu texto e inténtalo de nuevo.'
      : result.status === 'no_suggestion' ? 'No se sugieren cambios. Esto no garantiza que el texto sea correcto.'
        : result.status === 'partial' ? 'Revisión parcial: algunas frases no se han revisado.' : 'Sugerencia para revisar'}</p>
    <p className="text-sm text-slate-300">Tu texto: {result.original}</p>
    {result.suggested && <p>{result.suggested}</p>}
    <p className="text-xs text-slate-300">La revisión automática puede equivocarse. Compara los textos antes de cambiar el tuyo.</p>
  </div>
}

export function A2Sample() {
  const [data, setData] = useState<Sample | null>(null)
  const [state, setState] = useState<A2StudyState>({ language: 'es', reviewed: [], draft: '', original: '' })
  const [error, setError] = useState('')
  const [category, setCategory] = useState('Animales')
  const [selected, setSelected] = useState('0-0')
  const [definitions, setDefinitions] = useState<Record<string, { definition: string; example: string }>>({})
  const [loadingWord, setLoadingWord] = useState('')
  const [wordError, setWordError] = useState('')
  const [revealed, setRevealed] = useState(false)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [checked, setChecked] = useState<Record<number, boolean>>({})
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
  async function explain(id: string) {
    setLoadingWord(id); setWordError('')
    try {
      const result = await api.explainA2Word(id)
      setDefinitions(current => ({ ...current, [id]: result }))
    } catch { setWordError('No se pudo generar la explicación. Espera un momento y vuelve a intentarlo; también puedes elegir English.') }
    finally { setLoadingWord('') }
  }
  async function review(kind: 'grammar' | 'writing') {
    const text = kind === 'grammar' ? grammarText : state.draft
    setReviewing(kind); setReviewError('')
    try {
      const result = await api.correctA2Writing(text)
      if (kind === 'grammar') setGrammarResult(result)
      else {
        setWritingResult(result)
        if (!state.original) update({ original: text })
      }
    } catch { setReviewError('No se pudo revisar. Tu texto sigue aquí; inténtalo de nuevo.') }
    finally { setReviewing(null) }
  }
  if (!data) return <p className="p-8" role="status">{error || 'Cargando A2 · Unidad 1…'}</p>
  const word = data.words.find(item => item.id === selected)!
  const definition = definitions[word.id]
  const categories = [...new Set(data.words.map(item => item.category))]
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
      <section id="palabras" className={panel}>
        <h2 className="text-2xl font-bold">1. Aprende las palabras del libro</h2>
        <p className="mt-2 text-slate-300">Estudia 6–8 expresiones cada vez. Piensa en su significado antes de mostrarlo. {state.reviewed.length} de {data.words.length} entradas marcadas como practicadas; no es una nota de dominio.</p>
        <div className="mt-4 flex flex-wrap items-center gap-4">
          <label>Categoría <select className="ml-2 max-w-full rounded-lg bg-slate-900 p-2" value={category} onChange={e => {
            setCategory(e.target.value); setSelected(data.words.find(item => item.category === e.target.value)!.id); setRevealed(false); setWordError('')
          }}>{categories.map(item => <option key={item}>{item}</option>)}</select></label>
          <fieldset className="flex gap-3"><legend className="mb-1 text-sm text-slate-300">Aprender el significado en</legend>
            {(['es', 'en'] as const).map(lang => <label key={lang} className="flex gap-2"><input type="radio" name="language" checked={state.language === lang} onChange={() => update({ language: lang })} />{lang === 'es' ? 'Español sencillo' : 'English'}</label>)}
          </fieldset>
        </div>
        <div className="mt-4 flex max-h-48 flex-wrap gap-2 overflow-auto" aria-label="Palabras">
          {data.words.filter(item => item.category === category).map(item => <button key={item.id} aria-pressed={item.id === selected}
            className={item.id === selected ? button : secondary} onClick={() => { setSelected(item.id); setRevealed(false); setWordError('') }}>
            {item.text}{state.reviewed.includes(item.id) ? ' ✓' : ''}</button>)}
        </div>
        <div className="mt-5 rounded-2xl bg-slate-900 p-5">
          <p className="text-3xl font-bold">{word.text}</p>
          {!revealed ? <button className={`${button} mt-4`} onClick={() => setRevealed(true)}>Mostrar significado</button>
            : state.language === 'en' ? <p className="mt-4 text-xl" lang="en">{word.translation}</p>
              : definition ? <div className="mt-4 space-y-3"><p className="text-lg">{definition.definition}</p><p className="italic text-lime-200">{definition.example}</p><p className="text-xs text-slate-400">Explicación generada automáticamente; puede contener errores.</p></div>
                : <div className="mt-4"><button className={button} disabled={!!loadingWord} onClick={() => void explain(word.id)}>{loadingWord === word.id ? 'Preparando explicación…' : loadingWord ? 'Terminando otra explicación…' : 'Explicar en español'}</button><p className="mt-2 text-sm text-slate-300">La primera explicación puede tardar un poco.</p></div>}
          {wordError && <p role="alert" className="mt-3 text-orange-200">{wordError}</p>}
          <label className="mt-5 flex items-center gap-2"><input type="checkbox" checked={state.reviewed.includes(word.id)} onChange={e => update({ reviewed: e.target.checked ? [...state.reviewed, word.id] : state.reviewed.filter(id => id !== word.id) })} />He practicado esta expresión</label>
          <p className="mt-2 text-sm text-slate-300">Ahora úsala en una frase sobre ti. Por ejemplo: «Me gusta…», «Me cuesta…» o «Te recomiendo…».</p>
        </div>
      </section>
      <section id="gramatica" className={panel}>
        <h2 className="text-2xl font-bold">2. Entiende y practica la gramática</h2>
        <div className="my-4 grid gap-3 sm:grid-cols-2">
          <p><strong>Gustos:</strong> Me gusta leer. Me gustan los libros. El verbo cambia con la cosa que gusta.</p>
          <p><strong>Coincidir:</strong> Me gusta leer → A mí también. No me gusta correr → A mí tampoco.</p>
          <p><strong>Dificultad:</strong> Me cuesta hablar. Me cuestan las conversaciones rápidas.</p>
          <p><strong>Consejos:</strong> Puedes practicar. Te recomiendo escuchar. Hay que repetir. Usa el infinitivo.</p>
        </div>
        <div className="space-y-4">{data.grammar.map((item, index) => <div key={item.prompt} className="rounded-xl bg-slate-900 p-4">
          <label htmlFor={`grammar-${index}`} className="block font-semibold">{item.prompt}</label>
          <div className="mt-2 flex flex-wrap gap-2"><input id={`grammar-${index}`} className="min-w-0 rounded-lg bg-slate-700 p-2" value={answers[index] ?? ''} maxLength={100} onChange={e => { setAnswers({ ...answers, [index]: e.target.value }); setChecked({ ...checked, [index]: false }) }} /><button className={button} disabled={!answers[index]?.trim()} onClick={() => setChecked({ ...checked, [index]: true })}>Comprobar</button></div>
          {checked[index] && <p className="mt-2 text-lime-200" role="status">{answers[index].trim().toLocaleLowerCase('es') === item.answer ? 'Correcto. ' : `Respuesta: ${item.answer}. `}{item.rule}</p>}
        </div>)}</div>
        <label htmlFor="grammar-writing" className="mt-5 block font-bold">Ahora crea tres frases: un gusto, una dificultad y un consejo.</label>
        <textarea id="grammar-writing" className="mt-2 w-full rounded-xl bg-slate-900 p-3" rows={3} maxLength={2000} value={grammarText} onChange={e => { setGrammarText(e.target.value); setGrammarResult(null) }} placeholder="Me gustan… Me cuesta… Te recomiendo…" />
        <button className={button} disabled={!!reviewing || !grammarText.trim()} onClick={() => void review('grammar')}>{reviewing === 'grammar' ? 'Revisando…' : 'Revisar mis frases'}</button>
        {grammarResult && <WritingFeedback result={grammarResult} />}
      </section>
      <section id="escuchar" className={panel}>
        <h2 className="text-2xl font-bold">3. Escucha el libro</h2>
        <p className="mt-3">Pista 1 · ¿Cómo puedes encontrar personas con intereses en común? Escucha y busca qué aplicación reúne a personas para hacer deporte.</p>
        <TextbookAudio track={1} />
        <details><summary className="cursor-pointer text-lime-300">Comprobar después de escuchar</summary><p>Las aplicaciones ayudan a conocer gente. Timpik conecta a personas para practicar deportes; Meetup reúne grupos con intereses comunes. Son descripciones del libro, no recomendaciones actuales.</p></details>
        <p className="mt-6">Pista 2 · ¿Qué le cuesta a Jake? ¿Qué actividad recomienda la profesora para mejorar su acento? ¿Y para conocer gente?</p>
        <TextbookAudio track={2} />
        <details><summary className="cursor-pointer text-lime-300">Comprobar después de escuchar</summary><p>A Jake le cuesta hablar y entender a la gente. La profesora recomienda el taller de pronunciación y el café con Maca para conocer gente y conversar.</p></details>
      </section>
      <section id="usar" className={panel}>
        <h2 className="text-2xl font-bold">4. Usa lo que has aprendido</h2>
        <p className="mt-3">Conversación: preséntate, compara tus gustos, explica una dificultad y pide una recomendación. Intenta usar tres expresiones del glosario.</p>
        {data.lesson_id && <div className="my-4 flex flex-wrap gap-3"><Link className={button} to={`/practica/conversacion/${data.lesson_id}`}>Practicar el diálogo</Link><Link className={secondary} to={`/leccion/${data.lesson_id}/repetir-video`}>Escuchar y repetir</Link></div>}
        <label htmlFor="unit-writing" className="mt-6 block font-bold">Escribe a un compañero nuevo (unas 60–80 palabras)</label>
        <p className="mt-2 text-slate-300">Describe tu personalidad, dos intereses, una dificultad y una actividad para practicar juntos. Añade una recomendación. Usa palabras del glosario y las estructuras de esta unidad.</p>
        <textarea id="unit-writing" className="mt-3 w-full rounded-xl bg-slate-900 p-3" rows={7} maxLength={2000} value={state.draft} onChange={e => { update({ draft: e.target.value }); setWritingResult(null) }} placeholder="Hola, soy… Me interesa… Me cuesta…" />
        <button className={button} disabled={!!reviewing || !state.draft.trim()} onClick={() => void review('writing')}>{reviewing === 'writing' ? 'Revisando…' : 'Revisar mi texto'}</button>
        {writingResult && <WritingFeedback result={writingResult} />}
        {state.original && <details className="mt-4"><summary className="cursor-pointer text-lime-300">Comparar con mi primer borrador</summary><p className="mt-2 whitespace-pre-wrap">{state.original}</p></details>}
        <p className="mt-3 text-sm text-slate-300">Revisa las sugerencias y edita tu texto. Comprueba tú también si has incluido los gustos, la dificultad y la recomendación: la corrección no califica el contenido.</p>
      </section>
      {reviewError && <p role="alert" className="text-orange-200">{reviewError}</p>}
      <footer className="sticky bottom-20 rounded-2xl border border-slate-600 bg-slate-900 p-4 shadow-xl">
        <button className={button} disabled={saving} onClick={() => void save()}>{saving ? 'Guardando…' : 'Guardar vocabulario y borrador'}</button>
        <p className="mt-2 text-sm text-slate-300" role="status">{saveMessage || 'Guarda antes de salir. Tu idioma elegido, las palabras marcadas y el borrador se guardan en tu cuenta.'}</p>
      </footer>
    </div>
  </main>
}
