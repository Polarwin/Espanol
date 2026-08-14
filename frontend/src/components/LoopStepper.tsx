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
    <div className="grid grid-cols-4 rounded-2xl bg-paper px-2 py-3 shadow-soft sm:flex sm:items-center sm:px-8 sm:py-4">
      {STEPS.map((step, i) => {
        const state = i < currentIndex ? 'done' : i === currentIndex ? 'active' : 'upcoming'
        const Icon = step.icon
        return (
          <div key={step.key} className="flex min-w-0 flex-1 items-center last:flex-none">
            <div className="flex min-w-0 flex-1 flex-col items-center gap-1 sm:flex-row sm:gap-3">
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
                className={`text-[11px] font-bold sm:text-[15px] ${
                  state === 'active' ? 'text-terracotta' : state === 'done' ? 'text-ink' : 'text-ink/40'
                }`}
              >
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div className="relative mx-4 hidden h-[3px] flex-1 overflow-hidden rounded-full bg-ink/8 sm:block">
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
