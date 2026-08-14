import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { LessonSummary, User } from '../api/types'
import { preferredName } from '../api/types'
import { Chip } from '../components/Chip'
import { IconBook, IconChevronRight } from '../components/icons'

export function Lecciones() {
  const [lessons, setLessons] = useState<LessonSummary[]>([])
  const [error, setError] = useState('')
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => { api.getLessons().then(setLessons).catch(() => setError('No se pudieron cargar las lecciones.')); api.getMe().then(setUser).catch(() => {}) }, [])

  return (
    <div className="mx-auto max-w-5xl px-4 py-5 sm:px-8 sm:py-8">
      <div className="flex items-center gap-3"><span className="flex h-12 w-12 items-center justify-center rounded-full bg-river-soft text-river"><IconBook size={24} /></span><div><h1 className="font-display text-2xl font-bold sm:text-3xl">{user ? `${preferredName(user)}, tus lecciones` : 'Tus lecciones'}</h1><p className="font-semibold text-ink-soft">He elegido práctica A1–A2 para ayudarte a hablar con más confianza.</p></div></div>
      {error && <p className="mt-5 font-bold text-terracotta">{error}</p>}
      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {lessons.map((lesson) => (
          <Link key={lesson.id} to={`/leccion/${lesson.id}`} className="group flex flex-col rounded-3xl bg-paper p-5 shadow-soft transition hover:-translate-y-0.5 hover:shadow-card">
            <div className="flex items-center justify-between"><Chip tone={lesson.cefr_level === 'A1' ? 'leaf' : 'river'}>{lesson.cefr_level}</Chip><span className="text-sm font-bold text-ink-soft">{Math.max(1, Math.ceil(lesson.duration_seconds / 60))} min</span></div>
            <h2 className="mt-4 font-display text-xl font-bold">{lesson.title}</h2>
            <div className="mt-2 flex flex-wrap gap-1.5">{lesson.topics.map((topic) => <Chip key={topic} tone="cream">{topic}</Chip>)}</div>
            <span className="mt-5 flex items-center gap-1 text-sm font-bold text-terracotta">Abrir lección <IconChevronRight size={16} /></span>
          </Link>
        ))}
      </div>
    </div>
  )
}
