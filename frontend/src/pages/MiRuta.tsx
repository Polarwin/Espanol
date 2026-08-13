import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Progress, TodayPath } from '../api/types'
import { Chip } from '../components/Chip'
import { FeedbackPanel } from '../components/FeedbackPanel'
import { IconChart, IconChevronDown, IconFlame, IconSun } from '../components/icons'
import { LoopStepper } from '../components/LoopStepper'
import { RepeatPhraseCard } from '../components/RepeatPhraseCard'
import { VideoPlayer } from '../components/VideoPlayer'

function greeting(): string {
  const h = new Date().getHours()
  if (h < 12) return 'Buenos días'
  if (h < 20) return 'Buenas tardes'
  return 'Buenas noches'
}

export function MiRuta() {
  const [today, setToday] = useState<TodayPath | null>(null)
  const [progress, setProgress] = useState<Progress | null>(null)

  useEffect(() => {
    api.getTodayPath().then(setToday).catch(() => {})
    api.getProgress().then(setProgress).catch(() => {})
  }, [])

  if (!today) {
    return <div className="p-10 text-ink-soft">Cargando tu ruta…</div>
  }

  return (
    <div className="flex min-h-screen flex-col px-8 pb-6 pt-5">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sun">
            <IconSun size={26} />
          </span>
          <h1 className="font-display text-[22px] font-bold">
            {greeting()}, Maya
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <Chip tone="river" icon={<IconChart size={13} />}>
            {today.lesson.cefr_level} · ajustándose
          </Chip>
          <span className="flex items-center gap-1.5 text-[15px] font-bold text-terracotta">
            <IconFlame size={19} />
            {progress?.streak.days ?? 12} días
          </span>
          <button className="flex items-center gap-1.5" aria-label="Perfil">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-[linear-gradient(140deg,#c78d54,#7a4a2b)] font-display text-sm font-bold text-paper">
              M
            </span>
            <IconChevronDown size={15} className="text-ink-soft" />
          </button>
        </div>
      </header>

      {/* Main grid */}
      <div className="mt-5 flex flex-1 gap-6">
        <div className="flex min-w-0 flex-1 flex-col gap-4">
          <section className="rounded-3xl bg-paper p-5 shadow-soft">
            <h2 className="font-display text-[30px] font-bold">{today.lesson.title}</h2>
            <div className="mt-3">
              <VideoPlayer src={today.video_url} subtitle={today.subtitle} />
            </div>
            <p className="mt-2.5 text-[13px] font-semibold text-ink-soft">
              Clip {today.clip_index} de {today.total_clips} · 00:42
            </p>
          </section>

          <RepeatPhraseCard phraseId={`${today.lesson.id}-clip-${today.clip_index}`} />

          <div className="mt-1 flex justify-end">
            <Link
              to={`/leccion/${today.lesson.id}/prueba`}
              className="rounded-full bg-terracotta px-5 py-2.5 text-sm font-bold text-paper shadow-soft transition hover:bg-terracotta-dark"
            >
              Ir a la prueba de la lección
            </Link>
          </div>
        </div>

        <FeedbackPanel data={today} />
      </div>

      {/* Loop stepper */}
      <footer className="mt-5">
        <LoopStepper current={today.step} />
      </footer>
    </div>
  )
}
