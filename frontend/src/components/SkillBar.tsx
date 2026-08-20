import type { ReactNode } from 'react'

interface SkillBarProps {
  icon: ReactNode
  label: string
  value: number // 0-100
  barClass?: string
  iconClass?: string
}

export function SkillBar({ icon, label, value, barClass = 'bg-leaf', iconClass = 'bg-leaf-soft text-leaf' }: SkillBarProps) {
  const displayValue = Math.round(Math.min(100, Math.max(0, value)))
  return (
    <div className="flex items-center gap-3">
      <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${iconClass}`}>{icon}</span>
      <span className="w-28 shrink-0 text-sm font-semibold">{label}</span>
      <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-ink/8">
        <div
          className={`h-full rounded-full transition-[width] duration-700 ${barClass}`}
          style={{ width: `${displayValue}%` }}
        />
      </div>
      <span className="w-11 shrink-0 text-right text-sm font-bold tabular-nums">{displayValue}%</span>
    </div>
  )
}
