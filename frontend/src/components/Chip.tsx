import type { ReactNode } from 'react'

interface ChipProps {
  icon?: ReactNode
  children: ReactNode
  tone?: 'cream' | 'sun' | 'leaf' | 'river' | 'blush' | 'outline'
  className?: string
}

const tones: Record<NonNullable<ChipProps['tone']>, string> = {
  cream: 'bg-cream-deep text-ink-soft',
  sun: 'bg-sun-soft text-ink',
  leaf: 'bg-leaf-soft text-leaf',
  river: 'bg-river-soft text-river',
  blush: 'bg-blush text-terracotta',
  outline: 'border border-ink/10 bg-paper text-ink-soft',
}

export function Chip({ icon, children, tone = 'cream', className = '' }: ChipProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[13px] font-semibold ${tones[tone]} ${className}`}
    >
      {icon}
      {children}
    </span>
  )
}
