import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Progress, TodayPath, User } from '../api/types'
import { preferredName } from '../api/types'
import { Chip } from '../components/Chip'
import { ClipQuizCard } from '../components/ClipQuiz'
import { FeedbackPanel } from '../components/FeedbackPanel'
import { IconChart, IconFlame, IconSun } from '../components/icons'
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
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState('')
  const [advancing, setAdvancing] = useState(false)

  useEffect(() => {
    api.getTodayPath().then(setToday).catch(() => setError('No se pudo cargar tu ruta.'))
    api.getProgress().then(setProgress).catch(() => {})
    api.getMe().then(setUser).catch(() => {})
  }, [])

  if (!today) {
    return <div className="p-6 text-ink-soft">{error || 'Cargando tu ruta…'}{error && <button onClick={() => window.location.reload()} className="mt-4 block rounded-xl bg-terracotta px-4 py-2 font-bold text-paper">Reintentar</button>}</div>
  }

  const stageCopy = {
    mira: ['Mira el clip', 'Observa la situación; activa los subtítulos si los necesitas.', 'Ya lo he visto'],
    escucha: ['Escucha con atención', 'Reproduce el clip otra vez y céntrate en cómo suena.', 'Ya lo he escuchado'],
    comprueba: ['Comprueba tu comprensión', 'Elige el significado de lo que acabas de oír.', 'Continuar'],
    habla: ['Habla en voz alta', 'Graba la frase y compara tu pronunciación.', 'He practicado la frase'],
    adapta: ['Adapta y continúa', 'Revisa tu feedback; queda la conversación final de la unidad.', 'Continuar a la conversación'],
    conversa: ['Cierra con una conversación', 'Pon en práctica la unidad con Ana. Al terminar, pasas a la siguiente lección.', 'Hablar con Ana'],
  }[today.step]

  const advance = async () => {
    setAdvancing(true)
    setError('')
    try {
      setToday(await api.advancePath(today.step))
      setProgress(await api.getProgress())
    } catch {
      setError('No se pudo guardar este paso. Inténtalo de nuevo.')
    } finally {
      setAdvancing(false)
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-3.5rem)] flex-col px-4 pb-5 pt-4 sm:px-6 md:min-h-screen md:px-8 md:pb-6 md:pt-5">
      {/* Header */}
      <header className="flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex w-full flex-wrap items-center gap-2 sm:w-auto sm:gap-3">
          <span className="text-sun">
            <IconSun size={26} />
          </span>
          <h1 className="font-display text-[22px] font-bold">
            {greeting()}, {user ? preferredName(user) : 'amigo'}
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
          <div className="ml-auto hidden items-center gap-1.5 sm:flex" aria-label="Perfil">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-[linear-gradient(140deg,#c78d54,#7a4a2b)] font-display text-sm font-bold text-paper">
              {(user ? preferredName(user) : 'A').charAt(0).toUpperCase()}
            </span>
          </div>
        </div>
      </header>

      {/* Main grid */}
      <div className="mt-4 flex flex-1 flex-col gap-4 xl:flex-row xl:gap-6">
        <div className="flex min-w-0 flex-1 flex-col gap-4">
          <section className="rounded-3xl bg-paper p-4 shadow-soft sm:p-5">
            <h2 className="font-display text-2xl font-bold sm:text-[30px]">{today.lesson.title}</h2>
            <div className="mt-3">
              <VideoPlayer src={today.video_url} subtitle={today.subtitle.es} />
            </div>
            <p className="mt-2.5 text-[13px] font-semibold text-ink-soft">
              Clip {today.clip_index + 1} de {today.total_clips} · 00:42
            </p>
            <div className="mt-4 flex flex-col gap-3 rounded-2xl bg-cream p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-display text-lg font-bold">{stageCopy[0]}</p>
                <p className="text-sm font-semibold text-ink-soft">{stageCopy[1]}</p>
              </div>
              {today.step === 'conversa' ? (
                <Link
                  to={`/leccion/${today.lesson.id}/conversacion?desde=ruta`}
                  className="shrink-0 rounded-full bg-terracotta px-5 py-3 text-center text-sm font-bold text-paper shadow-soft transition hover:bg-terracotta-dark"
                >
                  {stageCopy[2]}
                </Link>
              ) : (
                <button
                  type="button"
                  onClick={() => void advance()}
                  disabled={advancing}
                  className="shrink-0 rounded-full bg-terracotta px-5 py-3 text-sm font-bold text-paper shadow-soft transition hover:bg-terracotta-dark disabled:cursor-wait disabled:opacity-60"
                >
                  {advancing ? 'Guardando…' : stageCopy[2]}
                </button>
              )}
            </div>
            {error && <p className="mt-2 text-sm font-bold text-terracotta">{error}</p>}
          </section>

          {today.step === 'comprueba' && today.quiz && (
            <ClipQuizCard quiz={today.quiz} />
          )}

          {today.step === 'habla' && (
            <RepeatPhraseCard
              phraseId={`${today.lesson.id}-clip-${today.clip_index}`}
              phrase={today.pronunciation_tip.phrase || today.subtitle.es}
              tip={today.pronunciation_tip.tip}
            />
          )}

          <div className="mt-1 flex">
            <Link
              to={`/leccion/${today.lesson.id}/prueba`}
              className="w-full rounded-full bg-terracotta px-5 py-3 text-center text-sm font-bold text-paper shadow-soft transition hover:bg-terracotta-dark sm:ml-auto sm:w-auto sm:py-2.5"
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
