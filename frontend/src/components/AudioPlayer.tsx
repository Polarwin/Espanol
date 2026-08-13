import { useEffect, useRef, useState } from 'react'
import { IconReplay, IconVolume } from './icons'
import { Waveform } from './Waveform'

interface AudioPlayerProps {
  src?: string
  durationSeconds?: number
  compact?: boolean
}

function format(s: number): string {
  const m = Math.floor(s / 60)
  return `${m}:${String(Math.floor(s % 60)).padStart(2, '0')}`
}

/**
 * Listening-exercise audio player: replay button, waveform scrubber, time
 * readout, volume icon. Falls back to a simulated clock when no audio file
 * is available (mock mode).
 */
export function AudioPlayer({ src, durationSeconds = 18, compact = false }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [playing, setPlaying] = useState(false)
  const [time, setTime] = useState(0)
  const duration = durationSeconds
  const hasAudio = Boolean(src)

  useEffect(() => {
    if (!playing || hasAudio) return
    const id = window.setInterval(() => {
      setTime((t) => {
        if (t + 0.25 >= duration) {
          setPlaying(false)
          return duration
        }
        return t + 0.25
      })
    }, 250)
    return () => window.clearInterval(id)
  }, [playing, hasAudio, duration])

  const replay = () => {
    setTime(0)
    if (hasAudio && audioRef.current) {
      audioRef.current.currentTime = 0
      void audioRef.current.play()
    } else {
      setPlaying(true)
    }
  }

  const seek = (frac: number) => {
    const t = frac * duration
    setTime(t)
    if (audioRef.current) audioRef.current.currentTime = t
  }

  return (
    <div className={`flex items-center gap-3 ${compact ? '' : 'rounded-2xl border border-ink/8 bg-paper p-3'}`}>
      {hasAudio && (
        <audio
          ref={audioRef}
          src={src}
          onTimeUpdate={(e) => setTime(e.currentTarget.currentTime)}
          onEnded={() => setPlaying(false)}
        />
      )}
      <button
        onClick={replay}
        aria-label="Escuchar de nuevo"
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-terracotta text-paper shadow-soft transition hover:bg-terracotta-dark"
      >
        <IconReplay size={17} />
      </button>
      <button
        className="flex flex-1 cursor-pointer items-center"
        aria-label="Barra de audio"
        onClick={(e) => {
          const rect = e.currentTarget.getBoundingClientRect()
          seek((e.clientX - rect.left) / rect.width)
        }}
      >
        <Waveform
          bars={compact ? 36 : 72}
          progress={duration > 0 ? time / duration : 0}
          height={compact ? 26 : 40}
          className="w-full"
        />
      </button>
      <span className="shrink-0 text-xs font-semibold tabular-nums text-ink-soft">
        {format(time)} / {format(duration)}
      </span>
      <IconVolume size={17} className="shrink-0 text-ink-soft" />
    </div>
  )
}
