import type { LoopStep } from '../api/types'
import { IconChart, IconEar, IconEye, IconMic } from './icons'

const STEPS: { key: LoopStep; label: string; icon: typeof IconEye }[] = [
  { key: 'mira', label: 'Mira', icon: IconEye },
  { key: 'escucha', label: 'Escucha', icon: IconEar },
  { key: 'habla', label: 'Habla', icon: IconMic },
  { key: 'adapta', label: 'Adapta', icon: IconChart },
]

/** Bottom stepper of the core loop: Mira → Escucha → Habla → Adapta. */
export function LoopStepper({ current }: { current: LoopStep }) {
  const currentIndex = STEPS.findIndex((s) => s.key === current)
  return (
    <div className="flex items-center rounded-2xl bg-paper px-8 py-4 shadow-soft">
      {STEPS.map((step, i) => {
        const state = i < currentIndex ? 'done' : i === currentIndex ? 'active' : 'upcoming'
        const Icon = step.icon
        return (
          <div key={step.key} className="flex flex-1 items-center last:flex-none">
            <div className="flex items-center gap-3">
              <span
                className={`flex items-center justify-center rounded-full ${
                  state === 'active'
                    ? 'h-11 w-11 bg-terracotta text-paper shadow-card'
                    : state === 'done'
                      ? 'h-9 w-9 bg-sun-soft text-sun'
                      : 'h-9 w-9 bg-cream-deep text-ink/35'
                }`}
              >
                <Icon size={state === 'active' ? 22 : 18} />
              </span>
              <span
                className={`text-[15px] font-bold ${
                  state === 'active' ? 'text-terracotta' : state === 'done' ? 'text-ink' : 'text-ink/40'
                }`}
              >
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div className="relative mx-4 h-[3px] flex-1 overflow-hidden rounded-full bg-ink/8">
                {i < currentIndex && <div className="absolute inset-0 rounded-full bg-sun" />}
                {i === currentIndex && <div className="absolute inset-y-0 left-0 w-1/2 rounded-full bg-terracotta" />}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
