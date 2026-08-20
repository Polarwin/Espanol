import { useCallback, useEffect, useRef, useState } from 'react'
import { Capacitor } from '@capacitor/core'

export type RecorderState = 'idle' | 'recording' | 'recorded' | 'error'

interface UseRecorderResult {
  state: RecorderState
  /** true while getUserMedia/MediaRecorder setup is in flight */
  starting: boolean
  error: string | null
  blob: Blob | null
  seconds: number
  start: () => Promise<void>
  stop: () => void
  reset: () => void
}

/** MediaRecorder wrapper for the "Repite la frase" pronunciation flow. */
export function useRecorder(): UseRecorderResult {
  const [state, setState] = useState<RecorderState>('idle')
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [blob, setBlob] = useState<Blob | null>(null)
  const [seconds, setSeconds] = useState(0)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<number | null>(null)
  const startingRef = useRef(false)

  const cleanup = useCallback(() => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current)
      timerRef.current = null
    }
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
  }, [])

  useEffect(() => cleanup, [cleanup])

  const start = useCallback(async () => {
    // No-op on double-tap: one mic stream / timer at a time.
    if (startingRef.current || recorderRef.current?.state === 'recording') return
    startingRef.current = true
    setStarting(true)
    setError(null)
    setBlob(null)
    if (typeof MediaRecorder === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      setError('Tu navegador no permite grabar audio.')
      setState('error')
      startingRef.current = false
      setStarting(false)
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const recorder = new MediaRecorder(stream)
      recorderRef.current = recorder
      chunksRef.current = []
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      recorder.onstop = () => {
        const type = recorder.mimeType || 'audio/webm'
        setBlob(new Blob(chunksRef.current, { type }))
        setState('recorded')
        cleanup()
      }
      recorder.start()
      setSeconds(0)
      timerRef.current = window.setInterval(() => setSeconds((s) => s + 1), 1000)
      setState('recording')
    } catch (reason) {
      const denied = reason instanceof DOMException && reason.name === 'NotAllowedError'
      setError(denied
        ? Capacitor.isNativePlatform()
          ? 'Permiso de micrófono denegado. Actívalo en Ajustes → Apps → ¡Vamos! Español → Permisos.'
          : 'Permiso de micrófono bloqueado. Pulsa el candado junto a la dirección web y permite el micrófono.'
        : 'No pudimos acceder al micrófono. Revisa que esté disponible.')
      setState('error')
      cleanup()
    } finally {
      startingRef.current = false
      setStarting(false)
    }
  }, [cleanup])

  const stop = useCallback(() => {
    if (recorderRef.current?.state === 'recording') recorderRef.current.stop()
  }, [])

  const reset = useCallback(() => {
    setBlob(null)
    setSeconds(0)
    setState('idle')
    setError(null)
  }, [])

  return { state, starting, error, blob, seconds, start, stop, reset }
}
