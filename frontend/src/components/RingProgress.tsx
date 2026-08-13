interface RingProgressProps {
  /** e.g. 4 */
  done: number
  /** e.g. 5 */
  total: number
  size?: number
  ringClass?: string
  pending?: boolean
  pendingLabel?: string
}

/** Circular ring indicator used in "Evaluación de hoy". */
export function RingProgress({
  done,
  total,
  size = 46,
  ringClass = 'stroke-leaf',
  pending = false,
  pendingLabel = 'pendiente',
}: RingProgressProps) {
  const stroke = 4
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const frac = total > 0 ? Math.min(1, done / total) : 0

  if (pending) {
    return (
      <span className="flex flex-col items-center gap-1">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            strokeWidth={stroke}
            strokeDasharray="3 5"
            className="stroke-ink/25"
            strokeLinecap="round"
          />
        </svg>
        <span className="text-[11px] font-semibold text-ink-soft">{pendingLabel}</span>
      </span>
    )
  }

  return (
    <span className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" strokeWidth={stroke} className="stroke-ink/10" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - frac)}
          className={`${ringClass} transition-[stroke-dashoffset] duration-700`}
        />
      </svg>
      <span className="absolute text-[11px] font-bold tabular-nums">
        {done}/{total}
      </span>
    </span>
  )
}
