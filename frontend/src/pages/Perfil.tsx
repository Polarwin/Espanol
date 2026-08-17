import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { User } from '../api/types'
import { preferredName } from '../api/types'

export function Perfil() {
  const [user, setUser] = useState<User | null>(null)
  const [displayName, setDisplayName] = useState('')
  const [nickname, setNickname] = useState('')
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)
  const [pickedLevel, setPickedLevel] = useState('')
  const [levelMessage, setLevelMessage] = useState('')
  const [changingLevel, setChangingLevel] = useState(false)

  useEffect(() => {
    api.getMe().then((profile) => {
      setUser(profile)
      setDisplayName(profile.display_name)
      setNickname(profile.nickname ?? '')
    }).catch(() => setMessage('No se pudo cargar tu perfil.'))
  }, [])

  async function save(event: FormEvent) {
    event.preventDefault()
    if (!displayName.trim()) return
    setSaving(true)
    setMessage('')
    try {
      const updated = await api.updateProfile(displayName.trim(), nickname.trim() || null)
      setUser(updated)
      setDisplayName(updated.display_name)
      setNickname(updated.nickname ?? '')
      setMessage(`¡Perfecto, ${preferredName(updated)}! Ya usaremos ese nombre.`)
    } catch {
      setMessage('No se pudo guardar. Inténtalo de nuevo.')
    } finally {
      setSaving(false)
    }
  }

  async function changeLevel() {
    if (!pickedLevel || changingLevel) return
    setChangingLevel(true)
    setLevelMessage('')
    try {
      const result = await api.setLevel(pickedLevel)
      setLevelMessage(`Tu nivel ahora es ${result.overall_level}. Tu ruta se ha ajustado.`)
      setPickedLevel('')
    } catch {
      setLevelMessage('No se pudo cambiar el nivel. Inténtalo de nuevo.')
    } finally {
      setChangingLevel(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-8 md:py-12">
      <p className="text-sm font-bold uppercase tracking-[0.18em] text-terracotta">Tu perfil</p>
      <h1 className="mt-2 font-display text-3xl font-bold sm:text-4xl">
        {user ? `¡Hola, ${preferredName(user)}!` : 'Tu nombre en ¡Vamos!'}
      </h1>
      <p className="mt-3 font-semibold text-ink-soft">
        Dinos cómo te llamas y cómo prefieres que te llamemos durante tus lecciones.
      </p>

      <form onSubmit={save} className="mt-8 rounded-3xl bg-paper p-5 shadow-card sm:p-7">
        <label className="block text-sm font-bold" htmlFor="display-name">Nombre</label>
        <input id="display-name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} maxLength={60} required className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 font-semibold outline-none focus:border-terracotta" placeholder="María García" />

        <label className="mt-5 block text-sm font-bold" htmlFor="nickname">Apodo o nombre preferido</label>
        <input id="nickname" value={nickname} onChange={(event) => setNickname(event.target.value)} maxLength={30} className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 font-semibold outline-none focus:border-terracotta" placeholder="Mari" />
        <p className="mt-2 text-sm font-semibold text-ink-soft">Si lo dejas vacío, te llamaremos por tu nombre.</p>

        <button disabled={saving || !displayName.trim()} className="mt-6 w-full rounded-xl bg-terracotta px-5 py-3 font-bold text-paper shadow-soft disabled:opacity-50 sm:w-auto">
          {saving ? 'Guardando…' : 'Guardar mi nombre'}
        </button>
        {message && <p className="mt-4 font-bold text-leaf" role="status">{message}</p>}
      </form>

      <section className="mt-6 rounded-3xl bg-paper p-5 shadow-card sm:p-7">
        <h2 className="font-display text-xl font-bold">Tu nivel</h2>
        <p className="mt-2 font-semibold text-ink-soft">
          Elige tu nivel directamente y tu ruta empezará desde ahí.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {['A1', 'A2', 'B1', 'B2', 'C1', 'C2'].map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => { setPickedLevel(item); setLevelMessage('') }}
              className={`rounded-full px-4 py-2 text-sm font-extrabold ${pickedLevel === item ? 'bg-terracotta text-paper' : 'bg-cream text-ink shadow-soft'}`}
            >
              {item}
            </button>
          ))}
        </div>
        {pickedLevel && (
          <button
            disabled={changingLevel}
            onClick={() => void changeLevel()}
            className="mt-4 rounded-xl bg-terracotta px-5 py-3 font-bold text-paper shadow-soft disabled:opacity-50"
          >
            {changingLevel ? 'Cambiando…' : `Cambiar a ${pickedLevel}`}
          </button>
        )}
        {levelMessage && <p className="mt-4 font-bold text-leaf" role="status">{levelMessage}</p>}
      </section>

      <section className="mt-6 rounded-3xl bg-paper p-5 shadow-card sm:p-7">
        <h2 className="font-display text-xl font-bold">Prueba de nivel</h2>
        <p className="mt-2 font-semibold text-ink-soft">
          ¿Has mejorado? Repite la prueba cuando quieras: es diferente cada vez y ajusta tu ruta a tu nivel real.
        </p>
        <Link to="/nivel" className="mt-4 inline-block rounded-xl bg-river px-5 py-3 font-bold text-paper shadow-soft">
          Hacer la prueba de nivel
        </Link>
      </section>
    </div>
  )
}
