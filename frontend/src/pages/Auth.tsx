import { useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { api, getToken, setToken } from '../api/client'

export function Auth() {
  const navigate = useNavigate()
  const [registering, setRegistering] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  if (getToken()) return <Navigate to="/" replace />

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      const result = registering
        ? await api.register(email, password, name, [])
        : await api.login(email, password)
      setToken(result.token); navigate('/')
    } catch { setError('No se pudo iniciar la sesión. Revisa los datos e inténtalo otra vez.') }
    finally { setBusy(false) }
  }

  return <main className="flex min-h-screen items-center justify-center bg-cream px-5">
    <form onSubmit={submit} className="w-full max-w-md rounded-3xl bg-paper p-8 shadow-card">
      <h1 className="font-display text-4xl font-bold">¡Vamos<span className="text-terracotta">!</span></h1>
      <p className="mt-2 font-semibold text-ink-soft">{registering ? 'Crea tu ruta personal de español.' : 'Continúa con tu ruta de aprendizaje.'}</p>
      {registering && <input required minLength={2} value={name} onChange={e => setName(e.target.value)} placeholder="Tu nombre" className="mt-6 w-full rounded-xl border border-ink/15 px-4 py-3" />}
      <input required type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Correo electrónico" className="mt-3 w-full rounded-xl border border-ink/15 px-4 py-3" />
      <input required minLength={8} type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Contraseña" className="mt-3 w-full rounded-xl border border-ink/15 px-4 py-3" />
      {error && <p className="mt-3 text-sm font-semibold text-terracotta">{error}</p>}
      <button disabled={busy} className="mt-5 w-full rounded-xl bg-terracotta py-3 font-bold text-paper disabled:opacity-50">{busy ? 'Un momento…' : registering ? 'Crear cuenta' : 'Entrar'}</button>
      <button type="button" onClick={() => setRegistering(v => !v)} className="mt-4 w-full text-sm font-bold text-river">{registering ? 'Ya tengo una cuenta' : 'Crear una cuenta nueva'}</button>
    </form>
  </main>
}
