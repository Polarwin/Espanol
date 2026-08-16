import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { LessonDetail, User } from '../api/types'
import { preferredName } from '../api/types'
import { Chip } from '../components/Chip'
import { IconMic } from '../components/icons'
import { VideoPlayer } from '../components/VideoPlayer'

export function Leccion() {
  const { lessonId } = useParams()
  const [lesson, setLesson] = useState<LessonDetail | null>(null)
  const [error, setError] = useState('')
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    if (!lessonId) return
    api.selectLesson(lessonId).catch(() => {})
    api.getLesson(lessonId, Date.now() % 1_000_000).then(setLesson).catch(() => setError('No se pudo cargar la lección.'))
    api.getMe().then(setUser).catch(() => {})
  }, [lessonId])

  if (!lesson) return <div className="p-6 font-semibold text-ink-soft">{error || 'Cargando la lección…'}</div>
  const firstLine = lesson.segments[0]?.transcript[0]?.es ?? lesson.title
  const cues = lesson.segments.flatMap((segment) => {
    const span = segment.end_seconds - segment.start_seconds
    return segment.transcript.map((line, index) => ({
      start: segment.start_seconds + (index * span) / segment.transcript.length,
      end: segment.start_seconds + ((index + 1) * span) / segment.transcript.length,
      text: line.es,
    }))
  })
  const vocabularyWords = new Set(lesson.vocabulary.map((item) => item.text))

  return (
    <div className="mx-auto max-w-4xl px-4 py-5 sm:px-8 sm:py-8">
      <div className="flex flex-wrap items-center gap-2"><Chip tone={lesson.cefr_level === 'A1' ? 'leaf' : 'river'}>{lesson.cefr_level}</Chip>{lesson.topics.map((topic) => <Chip key={topic} tone="cream">{topic}</Chip>)}</div>
      <h1 className="mt-3 font-display text-3xl font-bold sm:text-4xl">{lesson.title}</h1>
      <p className="mt-1 font-semibold text-ink-soft">{user ? `${preferredName(user)}, escucha el diálogo y activa los subtítulos si los necesitas. Después podrás practicarlo con tu propia voz.` : 'Escucha el diálogo y activa los subtítulos si los necesitas. Después podrás practicarlo con tu propia voz.'}</p>
      <div className="mt-4 grid gap-3 rounded-2xl border border-river/15 bg-river-soft p-4 sm:grid-cols-2"><div><p className="text-xs font-extrabold uppercase tracking-wide text-river">Tu misión de esta visita</p><p className="mt-1 font-semibold">{lesson.personal_welcome}</p><p className="mt-1 text-sm font-semibold text-ink-soft">{lesson.session_mission}</p></div><div className="rounded-xl bg-paper p-3"><p className="text-xs font-extrabold uppercase tracking-wide text-terracotta">Frase especial</p><p className="mt-1 font-display text-lg font-bold">«{lesson.focus_phrase}»</p></div></div>
      <div className="mt-5"><VideoPlayer src={lesson.video_url} subtitle={firstLine} cues={cues} /></div>
      <details className="mt-6 rounded-3xl bg-paper p-5 shadow-soft" open>
        <summary className="cursor-pointer list-none">
          <div className="flex items-center justify-between gap-3">
            <div><p className="text-xs font-extrabold uppercase tracking-wide text-river">Apéndice</p><h2 className="font-display text-xl font-bold">Vocabulario de la unidad</h2></div>
            <Chip tone="river">{lesson.vocabulary.length} palabras</Chip>
          </div>
        </summary>
        <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {lesson.vocabulary.map((item) => (
            <div key={item.text} className="rounded-2xl bg-cream-deep px-4 py-3">
              <p className="font-bold">{item.text}</p>
              <p className="mt-1 text-sm font-semibold text-ink-soft">{item.definition_es}</p>
              <p className="mt-2 text-sm italic text-ink">«{item.example_es}»</p>
              <details className="mt-2">
                <summary className="cursor-pointer text-xs font-extrabold text-river">Ver traducción</summary>
                <p className="mt-1 text-sm font-semibold text-ink-soft">{item.translation}</p>
              </details>
            </div>
          ))}
        </div>
      </details>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        {lesson.segments.map((segment, index) => (
          <section key={segment.id} className="rounded-3xl bg-paper p-5 shadow-soft">
            <h2 className="font-display text-xl font-bold">Parte {index + 1}</h2>
            <div className="mt-3 space-y-3">{segment.transcript.map((line, lineIndex) => <div key={`${segment.id}-${lineIndex}`}><p className="font-bold">{line.es}</p><p className="text-sm font-semibold text-ink-soft">{line.en}</p></div>)}</div>
            <div className="mt-4 border-t border-ink/8 pt-3"><p className="text-xs font-bold uppercase tracking-wide text-ink-soft">Frases clave</p><div className="mt-2 flex flex-wrap gap-2">{segment.phrases.filter((phrase) => !vocabularyWords.has(phrase.text)).map((phrase) => <span key={phrase.id} title={phrase.translation} className="rounded-full bg-sun-soft px-3 py-1 text-sm font-bold text-terracotta-dark">{phrase.text}</span>)}</div></div>
          </section>
        ))}
      </div>
      <div className="mt-5 rounded-2xl bg-sun-soft p-4"><p className="text-xs font-extrabold uppercase tracking-wide text-terracotta-dark">Reto personal</p><p className="mt-1 font-bold">{lesson.closing_challenge}</p></div>
      <div className="mt-6 grid gap-3 sm:ml-auto sm:flex sm:w-fit"><Link to={`/leccion/${lesson.id}/conversacion`} className="rounded-2xl border-2 border-terracotta px-6 py-3 text-center font-bold text-terracotta">Conversar sobre esta unidad</Link><Link to={`/leccion/${lesson.id}/prueba`} className="rounded-2xl bg-terracotta px-6 py-3.5 text-center font-bold text-paper shadow-card">{user ? `${preferredName(user)}, empezar la práctica` : 'Empezar la práctica'}</Link></div>
      <Link to={`/leccion/${lesson.id}/conversacion`} className="fixed bottom-[calc(4.5rem+env(safe-area-inset-bottom))] right-4 z-40 flex items-center gap-2 rounded-full bg-terracotta px-4 py-3 font-extrabold text-paper shadow-card md:hidden" aria-label="Conversar sobre esta unidad"><IconMic size={20} />Conversar</Link>
    </div>
  )
}
