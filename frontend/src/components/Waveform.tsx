import { useMemo } from 'react'

interface WaveformProps {
  bars?: number
  /** 0..1 portion of bars shown in the active color */
  progress?: number
  /** animate bars (recording in progress) */
  live?: boolean
  activeClass?: string
  idleClass?: string
  className?: string
  height?: number
}

/** Deterministic pseudo-random bar heights so the waveform looks organic. */
function barHeights(count: number): number[] {
  return Array.from({ length: count }, (_, i) => {
    const x = Math.sin(i * 12.9898 + 4.1414) * 43758.5453
    const frac = x - Math.floor(x)
    const envelope = 0.45 + 0.55 * Math.sin((i / count) * Math.PI)
    return 18 + frac * 82 * envelope
  })
}

export function Waveform({
  bars = 56,
  progress = 0,
  live = false,
  activeClass = 'bg-terracotta',
  idleClass = 'bg-ink/15',
  className = '',
  height = 44,
}: WaveformProps) {
  const heights = useMemo(() => barHeights(bars), [bars])
  const cutoff = Math.round(progress * bars)
  return (
    <div
      className={`flex items-center gap-[3px] ${className}`}
      style={{ height }}
      role="img"
      aria-label="Forma de onda de audio"
    >
      {heights.map((h, i) => (
        <span
          key={i}
          className={`w-[3px] rounded-full transition-colors ${i < cutoff || live ? activeClass : idleClass} ${
            live ? 'wave-bar-live' : ''
          }`}
          style={{
            height: `${h}%`,
            animationDelay: live ? `${(i % 12) * 80}ms` : undefined,
          }}
        />
      ))}
    </div>
  )
}
