import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { TodayPath } from '../api/types'
import { Chip } from '../components/Chip'
import { IconChevronRight, IconSun } from '../components/icons'

export function Inicio() {
  const [today, setToday] = useState<TodayPath | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getTodayPath().then(setToday).catch(() => setError('No se pudo cargar tu sesión de hoy.'))
  }, [])

  return (
    <div className="mx-auto flex min-h-[calc(100vh-3.5rem)] max-w-3xl flex-col items-center justify-center px-4 py-8 text-center sm:px-8">
      <span className="text-sun">
        <IconSun size={40} />
      </span>
      <h1 className="mt-4 font-display text-3xl font-bold leading-tight sm:text-[42px]">
        ¡Hola, Maya! <br /> Qué bueno verte de nuevo.
      </h1>
      <p className="mt-3 max-w-lg text-[16px] font-semibold text-ink-soft">
        Tu sesión de hoy dura unos 12 minutos: mira un clip, repite las frases y deja que tu ruta se
        ajuste sola.
      </p>
      {error && <p className="mt-5 font-bold text-terracotta">{error}</p>}

      {today && (
        <div className="mt-8 w-full max-w-md rounded-3xl bg-paper p-5 text-left shadow-card sm:p-6">
          <div className="flex items-center justify-between">
            <Chip tone="river">{today.lesson.cefr_level}</Chip>
            <span className="text-[13px] font-semibold text-ink-soft">
              Clip {today.clip_index} de {today.total_clips}
            </span>
          </div>
          <h2 className="mt-3 font-display text-[24px] font-bold">{today.lesson.title}</h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {today.lesson.topics.map((t) => (
              <Chip key={t} tone="cream">
                {t}
              </Chip>
            ))}
          </div>
          <Link
            to="/ruta"
            className="mt-5 flex w-full items-center justify-center gap-2 rounded-2xl bg-terracotta py-3.5 text-[16px] font-bold text-paper shadow-card transition hover:bg-terracotta-dark"
          >
            Continuar mi ruta
            <IconChevronRight size={17} />
          </Link>
        </div>
      )}
    </div>
  )
}
