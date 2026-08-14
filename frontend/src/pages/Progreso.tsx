import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Progress, WeeklyRecap } from '../api/types'
import { Chip } from '../components/Chip'
import {
  IconBook,
  IconCheck,
  IconClock,
  IconEar,
  IconFlame,
  IconFluency,
  IconGrammar,
  IconPencil,
  IconPron,
  IconPuzzle,
  IconSparkle,
} from '../components/icons'
import { SkillBar } from '../components/SkillBar'

const SKILL_STYLE: Record<string, { icon: typeof IconPron; bar: string; chip: string }> = {
  pronunciation: { icon: IconPron, bar: 'bg-leaf', chip: 'bg-leaf-soft text-leaf' },
  fluency: { icon: IconFluency, bar: 'bg-sun', chip: 'bg-sun-soft text-sun' },
  grammar: { icon: IconGrammar, bar: 'bg-leaf', chip: 'bg-leaf-soft text-leaf' },
  vocabulary: { icon: IconBook, bar: 'bg-terracotta', chip: 'bg-blush text-terracotta' },
  listening: { icon: IconEar, bar: 'bg-river', chip: 'bg-river-soft text-river' },
  writing: { icon: IconPencil, bar: 'bg-river', chip: 'bg-river-soft text-river' },
}
const FALLBACK_STYLE = { icon: IconPuzzle, bar: 'bg-sun', chip: 'bg-sun-soft text-sun' }

export function Progreso() {
  const [progress, setProgress] = useState<Progress | null>(null)
  const [recap, setRecap] = useState<WeeklyRecap | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getProgress().then(setProgress).catch(() => setError('No se pudo cargar tu progreso.'))
    api.getWeeklyRecap().then(setRecap).catch(() => {})
  }, [])

  if (!progress) {
    return <div className="p-6 text-ink-soft">{error || 'Cargando tu progreso…'}</div>
  }

  const goalPct = progress.weekly_goal.target > 0 ? (progress.weekly_goal.current / progress.weekly_goal.target) * 100 : 0

  return (
    <div className="mx-auto max-w-4xl px-4 pb-8 pt-5 sm:px-8 sm:pb-10 sm:pt-7">
      <h1 className="font-display text-[30px] font-bold">Tu progreso</h1>
      <p className="mt-1 text-[15px] font-semibold text-ink-soft">
        Cada habilidad avanza a su propio ritmo. Tienes {progress.lessons_completed_total} {progress.lessons_completed_total === 1 ? 'lección guardada' : 'lecciones guardadas'}.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Streak */}
        <section className="rounded-3xl bg-paper p-5 shadow-soft">
          <div className="flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-blush text-terracotta">
              <IconFlame size={24} />
            </span>
            <div>
              <p className="font-display text-[26px] font-bold leading-none">{progress.streak.days} días</p>
              <p className="mt-1 text-[13px] font-semibold text-ink-soft">Racha actual</p>
            </div>
          </div>
          <p className="mt-3 text-[13px] font-semibold text-ink-soft">
            Racha flexible: te quedan{' '}
            <span className="font-bold text-ink">{progress.streak.recovery_days_left} días de recuperación</span>{' '}
            esta semana. Un día de descanso no borra tu progreso.
          </p>
        </section>

        {/* Weekly goal */}
        <section className="rounded-3xl bg-paper p-5 shadow-soft">
          <div className="flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-leaf-soft text-leaf">
              <IconCheck size={22} />
            </span>
            <div>
              <p className="font-display text-[26px] font-bold leading-none">
                {progress.weekly_goal.current}/{progress.weekly_goal.target}
              </p>
              <p className="mt-1 text-[13px] font-semibold text-ink-soft">Meta semanal</p>
            </div>
          </div>
          <p className="mt-3 text-[13px] font-semibold text-ink-soft">{progress.weekly_goal.label}</p>
          <div className="mt-2 h-2.5 overflow-hidden rounded-full bg-ink/8">
            <div className="h-full rounded-full bg-leaf transition-[width] duration-700" style={{ width: `${goalPct}%` }} />
          </div>
        </section>

        {/* Weekly time */}
        <section className="rounded-3xl bg-paper p-5 shadow-soft">
          <div className="flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-sun-soft text-sun">
              <IconClock size={22} />
            </span>
            <div>
              <p className="font-display text-[26px] font-bold leading-none">{recap?.minutes ?? '–'} min</p>
              <p className="mt-1 text-[13px] font-semibold text-ink-soft">Esta semana</p>
            </div>
          </div>
          <p className="mt-3 text-[13px] font-semibold text-ink-soft">
            {recap ? `${recap.lessons_completed} lecciones · ${recap.words_learned} palabras nuevas` : 'Cargando…'}
          </p>
        </section>
      </div>

      {/* Per-skill bars */}
      <section className="mt-5 rounded-3xl bg-paper p-5 shadow-soft sm:p-6">
        <h2 className="font-display text-[21px] font-bold">Tus habilidades</h2>
        <div className="mt-4 flex flex-col gap-4">
          {progress.skills.map((s) => {
            const style = SKILL_STYLE[s.skill] ?? FALLBACK_STYLE
            return (
              <SkillBar
                key={s.skill}
                icon={<style.icon size={16} />}
                label={s.label}
                value={s.score}
                barClass={style.bar}
                iconClass={style.chip}
              />
            )
          })}
        </div>
      </section>

      {/* Weekly recap */}
      {recap && (
        <section className="mt-5 rounded-3xl bg-sun-soft p-5 shadow-soft sm:p-6">
          <div className="flex items-center gap-2.5">
            <span className="text-terracotta-dark">
              <IconSparkle size={20} />
            </span>
            <h2 className="font-display text-[21px] font-bold">Resumen de la semana</h2>
          </div>
          <p className="mt-3 text-[15px] font-semibold leading-relaxed">
            Esta semana estudiaste <span className="font-bold">{recap.minutes} minutos</span>, completaste{' '}
            <span className="font-bold">{recap.lessons_completed} lecciones</span> y aprendiste{' '}
            <span className="font-bold">{recap.words_learned} palabras</span>.
          </p>
          <ul className="mt-3 flex flex-col gap-1.5">
            {recap.improvements.map((imp) => (
              <li key={imp.skill} className="flex items-center gap-2 text-[14px] font-semibold text-ink-soft">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-leaf text-paper">
                  <IconCheck size={11} />
                </span>
                {imp.label}: +{imp.delta.toFixed(1)}
              </li>
            ))}
          </ul>
          <div className="mt-4 rounded-2xl bg-paper p-4">
            <p className="text-[14px] font-bold">Logro de la semana</p>
            <p className="mt-0.5 text-[14px] font-semibold text-ink-soft">{recap.achievement}</p>
          </div>
          <div className="mt-3 flex flex-col items-start gap-2 sm:flex-row">
            <Chip tone="outline" className="bg-paper">
              Para la próxima semana
            </Chip>
            <p className="flex-1 pt-1 text-[14px] font-semibold text-ink-soft">{recap.recommendation}</p>
          </div>
        </section>
      )}
    </div>
  )
}
