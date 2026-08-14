import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client'

export function useSpeechExample(phrase: string) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const objectUrlRef = useRef<string | null>(null)
  const [playing, setPlaying] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    api.getSpeechExample(phrase).then((blob) => {
      if (cancelled) return
      const url = URL.createObjectURL(blob)
      objectUrlRef.current = url
      const audio = new Audio(url)
      audio.preload = 'auto'
      audio.addEventListener('ended', () => setPlaying(false))
      audio.addEventListener('pause', () => setPlaying(false))
      audioRef.current = audio
    }).catch(() => {
      if (!cancelled) setError('No se pudo cargar el ejemplo.')
    }).finally(() => {
      if (!cancelled) setLoading(false)
    })

    return () => {
      cancelled = true
      audioRef.current?.pause()
      audioRef.current = null
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current)
      objectUrlRef.current = null
    }
  }, [phrase])

  const play = async () => {
    setError('')
    try {
      if (!audioRef.current) throw new Error('Audio is not loaded')
      audioRef.current.currentTime = 0
      await audioRef.current.play()
      setPlaying(true)
    } catch {
      setError('No se pudo reproducir el ejemplo.')
      setPlaying(false)
    }
  }

  return { play, playing, loading, error }
}
