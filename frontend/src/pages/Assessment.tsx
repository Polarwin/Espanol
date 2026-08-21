import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { AttemptResult, ExerciseGroup, LessonAssessment } from '../api/types'
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

const GROUP_STYLE: Record<
  ExerciseGroup['type'],
  { num: string; ring: string; icon: typeof IconBook; iconChip: string }
> = {
  vocabulary: { num: 'bg-leaf text-paper', ring: 'stroke-leaf', icon: IconBook, iconChip: 'bg-leaf-soft text-leaf' },
  grammar: { num: 'bg-sun text-paper', ring: 'stroke-sun', icon: IconPuzzle, iconChip: 'bg-sun-soft text-sun' },
  reading: { num: 'bg-sun text-paper', ring: 'stroke-sun', icon: IconGlobe, iconChip: 'bg-sun-soft text-sun' },
  writing: { num: 'bg-river text-paper', ring: 'stroke-river', icon: IconPencil, iconChip: 'bg-river-soft text-river' },
  listening: { num: 'bg-terracotta text-paper', ring: 'stroke-river', icon: IconEar, iconChip: 'bg-river-soft text-river' },
}

interface GroupProgress {
  answered: number
  correct: number
}

function emptyProgress(assessment: LessonAssessment): Record<string, GroupProgress> {
  return Object.fromEntries(assessment.groups.map((group) => [group.type, { answered: 0, correct: 0 }]))
}

function statusOf(group: ExerciseGroup, progress: GroupProgress, activeType: string) {
  if (group.type === activeType) return 'active'
  if (progress.answered === 0) return 'pending'
  if (progress.answered >= group.exercises.length) return 'done'
  return 'active'
}

export function Assessment() {
  const questionPanelRef = useRef<HTMLElement | null>(null)
  const { lessonId } = useParams()
  const [assessment, setAssessment] = useState<LessonAssessment | null>(null)
  const [lessonTitle, setLessonTitle] = useState('')
  const [cefr, setCefr] = useState('')
  const [currentLessonId, setCurrentLessonId] = useState(0)
  const [progress, setProgress] = useState<Record<string, GroupProgress>>({})
  const [groupIndex, setGroupIndex] = useState(0)
  const [exerciseIndex, setExerciseIndex] = useState(0)
  const [selected, setSelected] = useState<string | null>(null)
  const [result, setResult] = useState<AttemptResult | null>(null)
  const [checking, setChecking] = useState(false)
  const [finished, setFinished] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const id = lessonId ? Number(lessonId) : (await api.getTodayPath()).lesson.id
        const [a, lesson] = await Promise.all([api.getAssessment(id), api.getLesson(id)])
        if (cancelled) return
        setAssessment(a)
        setCurrentLessonId(id)
        setProgress(emptyProgress(a))
        setLessonTitle(lesson.title)
        setCefr(lesson.cefr_level)
      } catch {
        if (!cancelled) setError('No se pudo cargar la prueba. Inténtalo de nuevo.')
      }
    }
    void load()
    return () => { cancelled = true }
  }, [lessonId])

  const activeGroup = assessment?.groups[groupIndex] ?? null
  const exercise = activeGroup?.exercises[exerciseIndex] ?? null
  const isLastExercise = activeGroup ? exerciseIndex === activeGroup.exercises.length - 1 : false
  const answeredBefore = Object.values(progress).reduce((total, item) => total + item.answered, 0)

  const check = async () => {
    if (!exercise || selected === null) return
    setChecking(true)
    setError('')
    try {
      const r = await api.submitAttempt(exercise.id, selected)
      setResult(r)
      if (activeGroup) {
        setProgress((p) => ({
          ...p,
          [activeGroup.type]: {
            answered: (p[activeGroup.type]?.answered ?? 0) + 1,
            correct: (p[activeGroup.type]?.correct ?? 0) + (r.correct ? 1 : 0),
          },
        }))
      }
    } catch {
      setError('No se pudo guardar la respuesta. Comprueba la conexión e inténtalo otra vez.')
    } finally {
      setChecking(false)
    }
  }

  const next = async () => {
    setResult(null)
    setSelected(null)
    if (!isLastExercise) {
      setExerciseIndex((i) => i + 1)
    } else {
      const nextGroup = assessment?.groups.findIndex((group, candidateIndex) => {
        if (candidateIndex === groupIndex) return false
        return (progress[group.type]?.answered ?? 0) < group.exercises.length
      }) ?? -1
      if (nextGroup >= 0) {
        setGroupIndex(nextGroup)
        setExerciseIndex(progress[assessment!.groups[nextGroup].type]?.answered ?? 0)
      } else {
        setChecking(true)
        try {
          await api.completeLesson(currentLessonId)
          setFinished(true)
        } catch {
          setError('Tus respuestas están guardadas, pero no pudimos marcar la lección como completada. Inténtalo otra vez.')
        } finally {
          setChecking(false)
        }
      }
    }
  }

  const openGroup = (candidateIndex: number) => {
    if (!assessment || result) return
    const group = assessment.groups[candidateIndex]
    const answered = progress[group.type]?.answered ?? 0
    if (answered >= group.exercises.length) return
    setGroupIndex(candidateIndex)
    setExerciseIndex(answered)
    setSelected(null)
    setError('')
    window.setTimeout(() => {
      questionPanelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      document.getElementById('assessment-answer')?.focus()
    }, 0)
  }

  if (!assessment || !activeGroup) {
    return <div className="p-10 text-ink-soft">{error || 'Cargando la prueba…'}</div>
  }

  return (
    <div className="flex min-h-[calc(100vh-3.5rem)] flex-col px-4 pb-5 pt-4 sm:px-6 md:min-h-screen md:px-8 md:pt-6">
      {/* Header */}
      <header className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold sm:text-[30px]">Prueba de la lección</h1>
          <p className="mt-0.5 text-[15px] font-semibold text-ink-soft">
            {lessonTitle} · {cefr}
          </p>
        </div>
        <div className="flex flex-wrap gap-2.5">
          <Chip tone="sun" icon={<IconClock size={14} />} className="px-4 py-2 text-sm">
            {assessment.duration_minutes} min
          </Chip>
          <Chip tone="outline" className="bg-paper px-4 py-2 text-sm text-ink">
            {Math.min(answeredBefore + 1, assessment.total_questions)} de {assessment.total_questions}
          </Chip>
        </div>
      </header>

      {/* Main grid */}
      <div className="mt-5 flex flex-1 flex-col gap-4 lg:flex-row lg:gap-6">
        {/* Question card */}
        <section ref={questionPanelRef} className="min-w-0 scroll-mt-16 flex-1 rounded-3xl bg-paper p-4 shadow-soft sm:p-6">
          {finished ? (
            <div className="flex h-full flex-col items-center justify-center gap-3 py-10 text-center">
              <span className="flex h-14 w-14 items-center justify-center rounded-full bg-leaf text-paper">
                <IconCheck size={26} />
              </span>
              <h2 className="font-display text-[26px] font-bold">¡Prueba completada!</h2>
              <p className="max-w-md text-[15px] font-semibold text-ink-soft">
                Has respondido las {assessment.total_questions} preguntas. Tu ruta ya se ha ajustado
                con tus resultados de vocabulario, gramática, escritura y comprensión.
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
                  <span className={`flex h-11 w-11 items-center justify-center rounded-full text-paper ${GROUP_STYLE[activeGroup.type].num}`}>
                    {activeGroup.type === 'listening' ? <IconHeadphones size={21} /> : (() => { const Icon = GROUP_STYLE[activeGroup.type].icon; return <Icon size={21} /> })()}
                  </span>
                  <div>
                    <h2 className="font-display text-[21px] font-bold">{activeGroup.label}</h2>
                    <p className="text-sm font-semibold text-ink-soft">{activeGroup.instructions}</p>
                  </div>
                </div>

                {exercise.passage && (
                  <div className="mt-4 rounded-2xl border border-river/15 bg-river-soft/60 px-4 py-3">
                    <p className="text-[15px] font-semibold leading-relaxed text-ink">{exercise.passage}</p>
                  </div>
                )}

                {exercise.audio_url && <div className="mt-4"><AudioPlayer src={exercise.audio_url} /></div>}

                <p className="mt-5 text-[17px] font-bold">{exercise.prompt}</p>

                <div className="mt-3 flex flex-col gap-2.5">
                  {exercise.options?.map((opt) => {
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
                  {!exercise.options && (
                    activeGroup.type === 'writing' ? (
                      <textarea
                        id="assessment-answer"
                        value={selected ?? ''}
                        disabled={Boolean(result)}
                        onChange={(event) => setSelected(event.target.value)}
                        rows={5}
                        placeholder="Escribe tu respuesta…"
                        className="w-full resize-y rounded-2xl border-2 border-ink/10 bg-cream/40 px-4 py-3 font-semibold outline-none focus:border-river"
                      />
                    ) : (
                      <input
                        id="assessment-answer"
                        value={selected ?? ''}
                        disabled={Boolean(result)}
                        onChange={(event) => setSelected(event.target.value)}
                        placeholder="Escribe tu respuesta…"
                        className="w-full rounded-2xl border-2 border-ink/10 bg-cream/40 px-4 py-3 font-semibold outline-none focus:border-river"
                      />
                    )
                  )}
                </div>

                {result && (
                  <p className={`mt-3 text-sm font-bold ${result.correct ? 'text-leaf' : 'text-terracotta'}`}>
                    {result.feedback}
                  </p>
                )}
                {error && <p className="mt-3 text-sm font-bold text-terracotta">{error}</p>}

                {result ? (
                  <button
                    onClick={() => void next()}
                    disabled={checking}
                    className="mt-5 w-full rounded-2xl bg-terracotta py-3.5 text-[16px] font-bold text-paper shadow-card transition hover:bg-terracotta-dark"
                  >
                    {checking ? 'Guardando tu progreso…' : answeredBefore >= assessment.total_questions ? 'Terminar y guardar' : 'Siguiente pregunta'}
                  </button>
                ) : (
                  <button
                    onClick={check}
                    disabled={!selected?.trim() || checking}
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
        <aside className="flex w-full shrink-0 flex-col gap-4 lg:w-[290px]">
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
      <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4 xl:gap-4">
        {assessment.groups.map((g, i) => {
          const style = GROUP_STYLE[g.type]
          const p = progress[g.type] ?? { answered: 0, correct: 0 }
          const status = statusOf(g, p, activeGroup.type)
          return (
            <button
              type="button"
              key={g.type}
              onClick={() => openGroup(i)}
              disabled={status === 'done' || Boolean(result)}
              className={`rounded-3xl border-2 bg-paper p-4 text-left shadow-soft transition ${
                status === 'active' ? 'border-river' : 'border-transparent'
              } ${status === 'done' ? 'cursor-default' : 'hover:border-river/50 hover:shadow-card'} disabled:opacity-70`}
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
              {status !== 'done' && <p className="mt-3 text-sm font-bold text-river">{status === 'active' ? 'Respondiendo ahora' : 'Responder ahora'}</p>}
            </button>
          )
        })}
      </div>

      {/* Footer */}
      <footer className="mt-5 flex flex-wrap items-center gap-2 text-[13px] font-semibold text-ink-soft sm:gap-3">
        <IconBook size={16} />
        <span>Fuente de la lección</span>
        <Chip tone="outline" icon={<IconBuilding size={13} />} className="bg-paper">
          Biblioteca local
        </Chip>
        <Chip tone="outline" icon={<IconGlobe size={13} />} className="bg-paper">
          Contenido online revisado
        </Chip>
        <span className="flex w-full items-center gap-2 text-leaf sm:ml-auto sm:w-auto">
          <span className="flex h-5 w-5 items-center justify-center rounded-full border-2 border-leaf">
            <IconCheck size={11} />
          </span>
          Nuevas lecciones se añaden automáticamente
        </span>
      </footer>
    </div>
  )
}
