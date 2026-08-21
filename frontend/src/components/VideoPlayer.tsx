import { useEffect, useRef, useState } from 'react'
import { IconExpand, IconPause, IconPlay, IconVolume } from './icons'

interface CaptionCue {
  start: number
  end: number
  text: string
}

interface VideoPlayerProps {
  src?: string
  subtitle: string
  /** timed caption lines; when provided, the overlay follows playback time */
  cues?: CaptionCue[]
  /** Optional absolute bounds when playing one clip from a longer video. */
  startTime?: number
  endTime?: number
  /** fallback duration when there is no playable media (mock mode) */
  fallbackDuration?: number
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

/**
 * Video player matching the core-loop mockup: rounded dark frame, Spanish
 * subtitle overlay, and a custom control bar (play, volume, scrubber, CC,
 * fullscreen). Without a playable source it shows a warm placeholder scene
 * and simulates playback time.
 */
export function VideoPlayer({ src, subtitle, cues, startTime, endTime, fallbackDuration = 42 }: VideoPlayerProps) {
  const playerRef = useRef<HTMLDivElement | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const [playing, setPlaying] = useState(false)
  const [time, setTime] = useState(0)
  const [duration, setDuration] = useState(fallbackDuration)
  const [muted, setMuted] = useState(false)
  const [captions, setCaptions] = useState(false)
  const hasVideo = Boolean(src)
  const captionText = cues
    ? (cues.find((cue) => time >= cue.start && time < cue.end)?.text ?? '')
    : subtitle
  const poster = src?.includes('/charla-con-vecinos/')
    ? src.replace(/video\.mp4(?:\?.*)?$/, 'poster.png')
    : undefined

  // Reset playback state when the source changes so a previous clip's
  // time/duration never bleeds into the next one.
  useEffect(() => {
    setTime(startTime ?? 0)
    setDuration(fallbackDuration)
  }, [src, startTime, fallbackDuration])

  // Simulated clock for the placeholder (no media available in mock mode).
  useEffect(() => {
    if (!playing || hasVideo) return
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
  }, [playing, hasVideo, duration])

  const toggle = () => {
    const v = videoRef.current
    if (hasVideo && v) {
      if (v.paused) {
        if (endTime !== undefined && v.currentTime >= endTime - 0.05) v.currentTime = startTime ?? 0
        void v.play()
      }
      else v.pause()
    } else {
      if (time >= duration) setTime(0)
      setPlaying((p) => !p)
    }
  }

  const seek = (frac: number) => {
    const t = frac * duration
    setTime(t)
    if (videoRef.current) videoRef.current.currentTime = t
  }

  const progress = duration > 0 ? time / duration : 0

  return (
    <div ref={playerRef} className="overflow-hidden rounded-2xl bg-navy-deep shadow-card">
      <div className="relative aspect-video">
        {hasVideo ? (
          <video
            ref={videoRef}
            src={src}
            poster={poster}
            muted={muted}
            className="absolute inset-0 h-full w-full object-cover"
            onTimeUpdate={(e) => {
              setTime(e.currentTarget.currentTime)
              if (endTime !== undefined && e.currentTarget.currentTime >= endTime - 0.04) e.currentTarget.pause()
            }}
            onLoadedMetadata={(e) => {
              setDuration(e.currentTarget.duration || fallbackDuration)
              if (startTime !== undefined) { e.currentTarget.currentTime = startTime; setTime(startTime) }
            }}
            onPlay={() => setPlaying(true)}
            onPause={() => setPlaying(false)}
            onEnded={() => setPlaying(false)}
            playsInline
          />
        ) : (
          // Placeholder scene (mock mode): warm café gradient with silhouettes.
          <div className="absolute inset-0 bg-[linear-gradient(150deg,#2b1c12_0%,#6b3f24_35%,#b07040_60%,#e0a866_80%,#4a2c18_100%)]">
            <div className="absolute left-[12%] top-[28%] h-[55%] w-[22%] rounded-t-full bg-navy-deep/55 blur-[1px]" />
            <div className="absolute right-[14%] top-[24%] h-[60%] w-[24%] rounded-t-full bg-navy-deep/45 blur-[1px]" />
            <div className="absolute inset-x-0 bottom-0 h-1/4 bg-gradient-to-t from-black/60 to-transparent" />
            <div className="absolute right-4 top-3 rounded bg-black/40 px-2 py-1 text-[11px] font-semibold text-paper/80">
              CAFÉ de BARRIO
            </div>
          </div>
        )}

        {!playing && (
          <button
            type="button"
            onClick={toggle}
            aria-label="Reproducir vídeo"
            className="absolute left-1/2 top-1/2 z-10 flex h-16 w-16 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border-2 border-white/80 bg-terracotta/95 pl-1 text-paper shadow-xl transition hover:scale-105 hover:bg-terracotta-dark focus-visible:outline focus-visible:outline-4 focus-visible:outline-offset-4 focus-visible:outline-sun sm:h-20 sm:w-20"
          >
            <IconPlay size={28} />
          </button>
        )}

        {/* Spanish subtitle overlay */}
        {captions && captionText && <div className="absolute inset-x-0 bottom-14 flex justify-center px-6">
          <span className="rounded-lg bg-black/65 px-4 py-1.5 text-center text-[15px] font-semibold text-paper">
            {captionText}
          </span>
        </div>}
      </div>

      {/* Control bar */}
      <div className="flex items-center gap-3 bg-black/85 px-4 py-2.5 text-paper">
        <button
          onClick={toggle}
          className="flex h-8 w-8 items-center justify-center rounded-full transition hover:bg-white/15"
          aria-label={playing ? 'Pausar' : 'Reproducir'}
        >
          {playing ? <IconPause size={16} /> : <IconPlay size={16} />}
        </button>
        <button onClick={() => setMuted((value) => !value)} aria-label={muted ? 'Activar sonido' : 'Silenciar'} className={`hidden sm:block ${muted ? 'text-terracotta' : 'text-paper/80'}`}><IconVolume size={17} /></button>
        <div className="group relative h-4 flex-1">
          <div className="absolute inset-y-[6px] w-full rounded-full bg-white/25" />
          <div
            className="absolute inset-y-[6px] rounded-full bg-terracotta"
            style={{ width: `${progress * 100}%` }}
          />
          <div
            className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-paper shadow"
            style={{ left: `${progress * 100}%` }}
          />
          <input
            type="range"
            min={0}
            max={Math.max(duration, 1)}
            step={0.1}
            value={time}
            onChange={(e) => seek(Number(e.target.value) / Math.max(duration, 1))}
            aria-label="Barra de progreso"
            className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
          />
        </div>
        <span className="hidden text-[11px] font-semibold tabular-nums text-paper/85 sm:inline">
          {formatTime(time)} / {formatTime(duration)}
        </span>
        <button onClick={() => setCaptions((value) => !value)} aria-pressed={captions} className={`rounded border px-1 text-[10px] font-bold ${captions ? 'border-paper/50 text-paper' : 'border-paper/20 text-paper/40'}`}>CC</button>
        <button onClick={() => void playerRef.current?.requestFullscreen()} aria-label="Pantalla completa" className="text-paper/80"><IconExpand size={15} /></button>
      </div>
    </div>
  )
}
