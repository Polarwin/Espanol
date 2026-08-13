import { useCallback, useEffect, useRef, useState } from 'react'

export type RecorderState = 'idle' | 'recording' | 'recorded' | 'error'

interface UseRecorderResult {
  state: RecorderState
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
  const [error, setError] = useState<string | null>(null)
  const [blob, setBlob] = useState<Blob | null>(null)
  const [seconds, setSeconds] = useState(0)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<number | null>(null)

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
    setError(null)
    setBlob(null)
    if (typeof MediaRecorder === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      setError('Tu navegador no permite grabar audio.')
      setState('error')
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
    } catch {
      setError('No pudimos acceder al micrófono. Revisa los permisos.')
      setState('error')
      cleanup()
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

  return { state, error, blob, seconds, start, stop, reset }
}
