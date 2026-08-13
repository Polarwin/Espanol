import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { AttemptResult, ExerciseGroup, LessonAssessment, TodayPath } from '../api/types'
import { AudioPlayer } from '../components/AudioPlayer'
import { Chip } from '../components/Chip'
import {
  IconBook,
  IconBuilding,
  IconCheck,
  IconClock,
  IconEar,
  IconGlobe,
  IconHeadphones,
  IconPencil,
  IconPuzzle,
  IconTrend,
} from '../components/icons'
import { RingProgress } from '../components/RingProgress'
import { Waveform } from '../components/Waveform'

const GROUP_STYLE: Record<
  ExerciseGroup['type'],
  { num: string; ring: string; icon: typeof IconBook; iconChip: string }
> = {
  vocabulary: { num: 'bg-leaf text-paper', ring: 'stroke-leaf', icon: IconBook, iconChip: 'bg-leaf-soft text-leaf' },
  grammar: { num: 'bg-sun text-paper', ring: 'stroke-sun', icon: IconPuzzle, iconChip: 'bg-sun-soft text-sun' },
  writing: { num: 'bg-river text-paper', ring: 'stroke-river', icon: IconPencil, iconChip: 'bg-river-soft text-river' },
  listening: { num: 'bg-terracotta text-paper', ring: 'stroke-river', icon: IconEar, iconChip: 'bg-river-soft text-river' },
}

interface GroupProgress {
  answered: number
  correct: number
}

/** Seed state matches the mockup: an in-progress assessment session. */
function seedProgress(assessment: LessonAssessment): Record<string, GroupProgress> {
  const seeded: Record<string, GroupProgress> = {}
  for (const g of assessment.groups) {
    if (g.type === 'vocabulary') seeded[g.type] = { answered: g.exercises.length, correct: 4 }
    else if (g.type === 'grammar') seeded[g.type] = { answered: g.exercises.length, correct: 3 }
    else if (g.type === 'listening') seeded[g.type] = { answered: 2, correct: 2 }
    else seeded[g.type] = { answered: 0, correct: 0 }
  }
  return seeded
}

function statusOf(group: ExerciseGroup, progress: GroupProgress, activeType: string) {
  if (group.type === activeType) return 'active'
  if (progress.answered === 0) return 'pending'
  if (progress.answered >= group.exercises.length) return 'done'
  return 'active'
}

export function Assessment() {
  const { lessonId } = useParams()
  const [assessment, setAssessment] = useState<LessonAssessment | null>(null)
  const [lessonTitle, setLessonTitle] = useState('Charla con vecinos')
  const [cefr, setCefr] = useState('A2')
  const [progress, setProgress] = useState<Record<string, GroupProgress>>({})
  const [exerciseIndex, setExerciseIndex] = useState(0)
  const [answeredBefore, setAnsweredBefore] = useState(2)
  const [selected, setSelected] = useState<string | null>(null)
  const [result, setResult] = useState<AttemptResult | null>(null)
  const [checking, setChecking] = useState(false)
  const [finished, setFinished] = useState(false)

  useEffect(() => {
    const id = lessonId ?? 'lesson-charla-vecinos'
    api.getAssessment(id).then((a) => {
      setAssessment(a)
      setProgress(seedProgress(a))
    }).catch(() => {})
    api
      .getTodayPath()
      .then((t: TodayPath) => {
        setLessonTitle(t.lesson.title)
        setCefr(t.lesson.cefr_level)
      })
      .catch(() => {})
  }, [lessonId])

  const activeGroup = useMemo(
    () => assessment?.groups.find((g) => g.type === 'listening') ?? null,
    [assessment],
  )
  const exercise = activeGroup?.exercises[exerciseIndex] ?? null
  const isLastExercise = activeGroup ? exerciseIndex === activeGroup.exercises.length - 1 : false

  const check = async () => {
    if (!exercise || selected === null) return
    setChecking(true)
    try {
      const r = await api.submitAttempt(exercise.id, selected)
      setResult(r)
      if (activeGroup) {
        setProgress((p) => ({
          ...p,
          [activeGroup.type]: {
            answered: p[activeGroup.type].answered + 1,
            correct: p[activeGroup.type].correct + (r.correct ? 1 : 0),
          },
        }))
      }
      setAnsweredBefore((n) => n + 1)
    } finally {
      setChecking(false)
    }
  }

  const next = () => {
    setResult(null)
    setSelected(null)
    if (isLastExercise) setFinished(true)
    else setExerciseIndex((i) => i + 1)
  }

  if (!assessment || !activeGroup) {
    return <div className="p-10 text-ink-soft">Cargando la prueba…</div>
  }

  return (
    <div className="flex min-h-screen flex-col px-8 pb-5 pt-6">
      {/* Header */}
      <header className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-[30px] font-bold">Prueba de la lección</h1>
          <p className="mt-0.5 text-[15px] font-semibold text-ink-soft">
            {lessonTitle} · {cefr}
          </p>
        </div>
        <div className="flex gap-2.5">
          <Chip tone="sun" icon={<IconClock size={14} />} className="px-4 py-2 text-sm">
            {assessment.duration_minutes} min
          </Chip>
          <Chip tone="outline" className="bg-paper px-4 py-2 text-sm text-ink">
            {Math.min(answeredBefore + 1, assessment.total_questions)} de {assessment.total_questions}
          </Chip>
        </div>
      </header>

      {/* Main grid */}
      <div className="mt-5 flex flex-1 gap-6">
        {/* Question card */}
        <section className="min-w-0 flex-1 rounded-3xl bg-paper p-6 shadow-soft">
          {finished ? (
            <div className="flex h-full flex-col items-center justify-center gap-3 py-10 text-center">
              <span className="flex h-14 w-14 items-center justify-center rounded-full bg-leaf text-paper">
                <IconCheck size={26} />
              </span>
              <h2 className="font-display text-[26px] font-bold">¡Prueba completada!</h2>
              <p className="max-w-md text-[15px] font-semibold text-ink-soft">
                Comprendiste {progress.listening?.correct ?? 0} de {activeGroup.exercises.length} clips de audio.
                Tu ruta de mañana ya se está ajustando a tus resultados.
              </p>
              <Link
                to="/progreso"
                className="mt-3 rounded-full bg-terracotta px-6 py-2.5 text-sm font-bold text-paper shadow-soft transition hover:bg-terracotta-dark"
              >
                Ver mi progreso
              </Link>
            </div>
          ) : (
            exercise && (
              <>
                <div className="flex items-center gap-3">
                  <span className="flex h-11 w-11 items-center justify-center rounded-full bg-terracotta text-paper">
                    <IconHeadphones size={21} />
                  </span>
                  <div>
                    <h2 className="font-display text-[21px] font-bold">Comprensión auditiva</h2>
                    <p className="text-sm font-semibold text-ink-soft">{activeGroup.instructions}</p>
                  </div>
                </div>

                <div className="mt-4">
                  <AudioPlayer src={exercise.audio_url} />
                </div>

                <p className="mt-5 text-[17px] font-bold">{exercise.prompt}</p>

                <div className="mt-3 flex flex-col gap-2.5">
                  {(exercise.options ?? []).map((opt) => {
                    const isSelected = selected === opt
                    const showWrong = result && isSelected && !result.correct
                    return (
                      <button
                        key={opt}
                        disabled={Boolean(result)}
                        onClick={() => setSelected(opt)}
                        className={`flex items-center gap-3 rounded-2xl border-2 px-4 py-3 text-left text-[15px] font-semibold transition ${
                          result && isSelected && result.correct
                            ? 'border-leaf bg-leaf-soft text-leaf'
                            : showWrong
                              ? 'border-terracotta bg-blush text-terracotta'
                              : isSelected
                                ? 'border-river bg-river-soft'
                                : 'border-ink/10 hover:border-ink/25'
                        }`}
                      >
                        <span
                          className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 ${
                            result && isSelected && result.correct
                              ? 'border-leaf bg-leaf'
                              : showWrong
                                ? 'border-terracotta bg-terracotta'
                                : isSelected
                                  ? 'border-terracotta'
                                  : 'border-ink/25'
                          }`}
                        >
                          {isSelected && (
                            <span className={`h-2 w-2 rounded-full ${result?.correct ? 'bg-paper' : 'bg-terracotta'}`} />
                          )}
                        </span>
                        {opt}
                      </button>
                    )
                  })}
                </div>

                {result && (
                  <p className={`mt-3 text-sm font-bold ${result.correct ? 'text-leaf' : 'text-terracotta'}`}>
                    {result.feedback}
                  </p>
                )}

                {result ? (
                  <button
                    onClick={next}
                    className="mt-5 w-full rounded-2xl bg-terracotta py-3.5 text-[16px] font-bold text-paper shadow-card transition hover:bg-terracotta-dark"
                  >
                    {isLastExercise ? 'Terminar la prueba' : 'Siguiente pregunta'}
                  </button>
                ) : (
                  <button
                    onClick={check}
                    disabled={selected === null || checking}
                    className="mt-5 w-full rounded-2xl bg-terracotta py-3.5 text-[16px] font-bold text-paper shadow-card transition hover:bg-terracotta-dark disabled:cursor-not-allowed disabled:opacity-45"
                  >
                    {checking ? 'Comprobando…' : 'Comprobar respuesta'}
                  </button>
                )}
              </>
            )
          )}
        </section>

        {/* Right panel */}
        <aside className="flex w-[290px] shrink-0 flex-col gap-4">
          <section className="rounded-3xl bg-paper p-5 shadow-soft">
            <h3 className="font-display text-[19px] font-bold">Evaluación de hoy</h3>
            <div className="mt-3 flex flex-col divide-y divide-ink/6">
              {assessment.groups.map((g) => {
                const style = GROUP_STYLE[g.type]
                const p = progress[g.type] ?? { answered: 0, correct: 0 }
                const pending = p.answered === 0
                return (
                  <div key={g.type} className="flex items-center gap-3 py-3">
                    <span className={`flex h-9 w-9 items-center justify-center rounded-full ${style.iconChip}`}>
                      <style.icon size={17} />
                    </span>
                    <span className="flex-1 text-[15px] font-semibold">{g.label}</span>
                    {pending ? (
                      <RingProgress done={0} total={g.exercises.length} pending pendingLabel="pendiente" />
                    ) : (
                      <RingProgress done={p.correct} total={g.exercises.length} ringClass={style.ring} />
                    )}
                  </div>
                )
              })}
            </div>
          </section>

          <section className="rounded-3xl bg-river-soft/60 p-5 shadow-soft">
            <div className="flex items-center gap-2.5">
              <span className="text-river">
                <IconTrend size={20} />
              </span>
              <h3 className="font-display text-[17px] font-bold">Tu ruta se está ajustando</h3>
            </div>
            <p className="mt-2 text-[13.5px] font-semibold text-ink-soft">
              Necesitas más práctica con el futuro próximo y el vocabulario de planes.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {['ir a + infinitivo', 'planes', 'fin de semana'].map((c) => (
                <Chip key={c} tone="outline" className="border-river/20 bg-paper text-river">
                  {c}
                </Chip>
              ))}
            </div>
          </section>
        </aside>
      </div>

      {/* Exercise strip */}
      <div className="mt-5 grid grid-cols-4 gap-4">
        {assessment.groups.map((g, i) => {
          const style = GROUP_STYLE[g.type]
          const p = progress[g.type] ?? { answered: 0, correct: 0 }
          const status = statusOf(g, p, activeGroup.type)
          return (
            <div
              key={g.type}
              className={`rounded-3xl border-2 bg-paper p-4 shadow-soft ${
                status === 'active' ? 'border-river' : 'border-transparent'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className={`flex h-7 w-7 items-center justify-center rounded-full text-[13px] font-bold ${style.num}`}>
                    {i + 1}
                  </span>
                  <span className="text-[15px] font-bold">{g.label}</span>
                </div>
                {status === 'done' ? (
                  <span className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-leaf text-leaf">
                    <IconCheck size={13} />
                  </span>
                ) : status === 'active' ? (
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-river text-paper">
                    <IconCheck size={13} />
                  </span>
                ) : (
                  <span className="h-6 w-6 rounded-full border-2 border-dashed border-ink/25" />
                )}
              </div>
              <p className="mt-1.5 text-[13px] font-semibold text-ink-soft">{g.instructions}</p>
              <GroupPreview group={g} />
            </div>
          )
        })}
      </div>

      {/* Footer */}
      <footer className="mt-5 flex items-center gap-3 text-[13px] font-semibold text-ink-soft">
        <IconBook size={16} />
        <span>Fuente de la lección</span>
        <Chip tone="outline" icon={<IconBuilding size={13} />} className="bg-paper">
          Biblioteca local
        </Chip>
        <Chip tone="outline" icon={<IconGlobe size={13} />} className="bg-paper">
          Contenido online revisado
        </Chip>
        <span className="ml-auto flex items-center gap-2 text-leaf">
          <span className="flex h-5 w-5 items-center justify-center rounded-full border-2 border-leaf">
            <IconCheck size={11} />
          </span>
          Nuevas lecciones se añaden automáticamente
        </span>
      </footer>
    </div>
  )
}

function GroupPreview({ group }: { group: ExerciseGroup }) {
  if (group.type === 'vocabulary') {
    return (
      <div className="mt-3 flex items-center gap-2">
        <Chip tone="leaf">quedar</Chip>
        <span className="h-[2px] w-6 rounded bg-ink/20" />
        <Chip tone="leaf">reunirse</Chip>
      </div>
    )
  }
  if (group.type === 'grammar') {
    return (
      <p className="mt-3 text-[13px] font-semibold">
        Este sábado{' '}
        <span className="mx-1 inline-block w-12 rounded-lg border border-ink/15 bg-cream px-2 py-0.5 text-center text-ink-soft">
          &nbsp;
        </span>{' '}
        a visitar Madrid.
      </p>
    )
  }
  if (group.type === 'writing') {
    return (
      <div className="mt-3 rounded-2xl border border-dashed border-ink/15 p-3">
        <p className="font-display text-[13px] italic text-ink-soft">Este fin de semana voy a…</p>
        <p className="mt-2 text-right text-[11px] font-bold text-ink-soft">0/4 frases</p>
      </div>
    )
  }
  return (
    <div className="mt-3 flex items-center gap-2">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-river text-paper">
        <IconEar size={13} />
      </span>
      <Waveform bars={26} height={20} progress={0.3} activeClass="bg-river" className="flex-1" />
      <span className="shrink-0 text-[10px] font-bold tabular-nums text-ink-soft">0:00 / 0:18</span>
    </div>
  )
}
