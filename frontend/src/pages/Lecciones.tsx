import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { LessonSummary, User } from '../api/types'
import { preferredName } from '../api/types'
import { Chip } from '../components/Chip'
import { IconBook, IconChevronRight } from '../components/icons'

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] as const

type CatalogLesson = LessonSummary & { unit: number }

function curriculum(lessons: LessonSummary[]): CatalogLesson[] {
  return LEVELS.flatMap((level) =>
    lessons
      .filter((lesson) => lesson.cefr_level === level)
      .map((lesson, index) => ({ ...lesson, unit: index + 1 })),
  )
}

function lessonName(lesson: CatalogLesson) {
  return lesson.title
    .replace(/^(?:A1|A2|B1|B2|C1|C2) · Unidad \d+: /, '')
    .replace(/^Vitamina A2 · U\d+: /, '')
}

function tone(level: string): 'leaf' | 'river' | 'sun' {
  if (level === 'A1') return 'leaf'
  if (level === 'B1') return 'sun'
  return 'river'
}

function LessonCard({ lesson, current = false }: { lesson: CatalogLesson; current?: boolean }) {
  return (
    <Link
      to={`/leccion/${lesson.id}`}
      className={`group flex flex-col rounded-3xl bg-paper p-5 shadow-soft transition hover:-translate-y-0.5 hover:shadow-card ${current ? 'ring-2 ring-terracotta ring-offset-2 ring-offset-cream' : ''}`}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Chip tone={tone(lesson.cefr_level)}>{lesson.cefr_level} · U{lesson.unit}</Chip>
          {current && <span className="text-xs font-extrabold uppercase tracking-wide text-terracotta">Tu unidad</span>}
        </div>
        <span className="text-sm font-bold text-ink-soft">{Math.max(1, Math.ceil(lesson.duration_seconds / 60))} min</span>
      </div>
      <h2 className="mt-4 font-display text-xl font-bold">{lessonName(lesson)}</h2>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {lesson.topics.filter((topic) => topic !== 'Vitamina companion').slice(0, 3).map((topic) => <Chip key={topic} tone="cream">{topic}</Chip>)}
      </div>
      <span className="mt-5 flex items-center gap-1 text-sm font-bold text-terracotta">Abrir unidad <IconChevronRight size={16} /></span>
    </Link>
  )
}

export function Lecciones() {
  const [lessons, setLessons] = useState<LessonSummary[]>([])
  const [currentId, setCurrentId] = useState<number | null>(null)
  const [showAll, setShowAll] = useState(false)
  const [level, setLevel] = useState<(typeof LEVELS)[number] | 'Todos'>('Todos')
  const [error, setError] = useState('')
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    Promise.all([api.getLessons(), api.getTodayPath(), api.getMe()])
      .then(([catalog, today, me]) => {
        setLessons(catalog)
        setCurrentId(today.lesson.id)
        setUser(me)
      })
      .catch(() => setError('No se pudieron cargar las lecciones.'))
  }, [])

  const ordered = useMemo(() => curriculum(lessons), [lessons])
  const currentIndex = Math.max(0, ordered.findIndex((lesson) => lesson.id === currentId))
  const windowStart = Math.max(0, Math.min(currentIndex - 1, ordered.length - 3))
  const nearby = ordered.slice(windowStart, windowStart + 3)
  const visibleAll = level === 'Todos' ? ordered : ordered.filter((lesson) => lesson.cefr_level === level)
  const current = ordered[currentIndex]

  return (
    <div className="mx-auto max-w-5xl px-4 py-5 sm:px-8 sm:py-8">
      <div className="flex items-center gap-3">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-river-soft text-river"><IconBook size={24} /></span>
        <div>
          <h1 className="font-display text-2xl font-bold sm:text-3xl">{user ? `${preferredName(user)}, tus unidades` : 'Tus unidades'}</h1>
          <p className="font-semibold text-ink-soft">{current ? `Continuamos cerca de ${current.cefr_level} · Unidad ${current.unit}.` : 'Tu ruta desde A1 hasta C2.'}</p>
        </div>
      </div>
      {error && <p className="mt-5 font-bold text-terracotta">{error}</p>}

      {!showAll && (
        <section className="mt-6">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div><p className="text-xs font-extrabold uppercase tracking-wide text-terracotta">Continúa por aquí</p><h2 className="font-display text-xl font-bold">Tu unidad anterior, actual y siguiente</h2></div>
            <button type="button" onClick={() => setShowAll(true)} className="rounded-full border border-river/25 bg-paper px-4 py-2 text-sm font-extrabold text-river shadow-soft">Elegir otra unidad</button>
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {nearby.map((lesson) => <LessonCard key={lesson.id} lesson={lesson} current={lesson.id === currentId} />)}
          </div>
        </section>
      )}

      {showAll && (
        <section className="mt-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {(['Todos', ...LEVELS] as const).map((item) => (
                <button key={item} type="button" onClick={() => setLevel(item)} className={`rounded-full px-4 py-2 text-sm font-extrabold ${level === item ? 'bg-terracotta text-paper' : 'bg-paper text-ink shadow-soft'}`}>{item}</button>
              ))}
            </div>
            <button type="button" onClick={() => setShowAll(false)} className="text-sm font-extrabold text-river">Volver a mi ruta</button>
          </div>
          <p className="mt-3 font-semibold text-ink-soft">Elige libremente entre las {visibleAll.length} unidades disponibles.</p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {visibleAll.map((lesson) => <LessonCard key={lesson.id} lesson={lesson} current={lesson.id === currentId} />)}
          </div>
        </section>
      )}
    </div>
  )
}
