import type { TodayPath } from '../api/types'
import { Chip } from './Chip'
import {
  IconChevronRight,
  IconCup,
  IconFluency,
  IconGrammar,
  IconMouth,
  IconPron,
  IconRocket,
  IconSpeaker,
  IconSuitcase,
  IconX,
  IconCheck,
} from './icons'
import { SkillBar } from './SkillBar'

const topicIcons: Record<string, typeof IconSuitcase> = {
  Viajes: IconSuitcase,
  'Vida diaria': IconCup,
}

/** Right-hand "Tu feedback" panel of the core-loop screen. */
export function FeedbackPanel({ data }: { data: TodayPath }) {
  const { feedback, pronunciation_tip: pron, grammar_tip: gram, next } = data
  return (
    <aside className="flex w-full shrink-0 flex-col gap-4 xl:w-[300px]">
      <section className="rounded-3xl bg-paper p-5 shadow-soft">
        <h3 className="font-display text-[19px] font-bold">Tu feedback</h3>
        <div className="mt-4 flex flex-col gap-3.5">
          <SkillBar
            icon={<IconPron size={16} />}
            label="Pronunciación"
            value={feedback.pronunciation}
            barClass="bg-leaf"
            iconClass="bg-leaf-soft text-leaf"
          />
          <SkillBar
            icon={<IconFluency size={16} />}
            label="Fluidez"
            value={feedback.fluidez}
            barClass="bg-sun"
            iconClass="bg-sun-soft text-sun"
          />
          <SkillBar
            icon={<IconGrammar size={16} />}
            label="Gramática"
            value={feedback.gramatica}
            barClass="bg-leaf"
            iconClass="bg-leaf-soft text-leaf"
          />
        </div>
      </section>

      <section className="rounded-3xl bg-paper p-5 shadow-soft">
        <h4 className="text-xs font-bold uppercase tracking-wide text-ink-soft">Pronunciación</h4>
        <div className="mt-3 flex items-center gap-3 rounded-2xl border border-ink/8 p-3">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blush text-terracotta">
            <IconMouth size={22} />
          </span>
          <div className="min-w-0 flex-1">
            <p className="font-display text-[17px] font-bold">
              {pron.phrase.split(' ').map((w) =>
                w === 'de' ? (
                  <mark key={w} className="rounded bg-sun-soft px-1 text-terracotta-dark">
                    {w}
                  </mark>
                ) : (
                  <span key={w}> {w} </span>
                ),
              )}
            </p>
            <p className="text-[13px] font-semibold text-ink-soft">{pron.tip}</p>
          </div>
          <button
            aria-label="Escuchar ejemplo"
            onClick={() => {
              window.speechSynthesis.cancel()
              const utterance = new SpeechSynthesisUtterance(pron.phrase)
              utterance.lang = 'es-ES'
              window.speechSynthesis.speak(utterance)
            }}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-river-soft text-river transition hover:bg-river hover:text-paper"
          >
            <IconSpeaker size={17} />
          </button>
        </div>

        <h4 className="mt-5 text-xs font-bold uppercase tracking-wide text-ink-soft">Gramática</h4>
        <div className="mt-3 flex flex-col gap-2">
          <p className="flex items-center gap-2 text-[15px] font-semibold text-terracotta line-through decoration-2">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-terracotta text-paper">
              <IconX size={11} />
            </span>
            {gram.wrong}
          </p>
          <p className="flex items-center gap-2 text-[15px] font-bold text-leaf">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-leaf text-paper">
              <IconCheck size={11} />
            </span>
            {gram.right}
          </p>
          <p className="text-[13px] font-semibold text-ink-soft">{gram.explanation}</p>
        </div>
      </section>

      <section className="rounded-3xl bg-sun-soft p-5 shadow-soft">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-sun/25 text-terracotta-dark">
            <IconRocket size={22} />
          </span>
          <div className="min-w-0 flex-1">
            <p className="font-display text-[17px] font-bold">{next.label}</p>
            <p className="text-[13px] font-semibold text-ink-soft">{next.description}</p>
          </div>
          <IconChevronRight size={18} className="shrink-0 text-ink-soft" />
        </div>
        <div className="mt-3 flex gap-2">
          {next.topics.map((t) => {
            const TopicIcon = topicIcons[t] ?? IconCup
            return (
              <Chip key={t} icon={<TopicIcon size={13} />} tone="outline" className="bg-paper">
                {t}
              </Chip>
            )
          })}
        </div>
      </section>
    </aside>
  )
}
