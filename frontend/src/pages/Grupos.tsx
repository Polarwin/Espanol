import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api/client'
import type { FriendGroup, User } from '../api/types'
import { IconSparkle } from '../components/icons'

export function Grupos() {
  const [groups, setGroups] = useState<FriendGroup[]>([])
  const [me, setMe] = useState<User | null>(null)
  const [name, setName] = useState('')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.getGroups().then(setGroups).catch(() => setError('No se pudieron cargar tus grupos.'))
    api.getMe().then(setMe).catch(() => {})
  }, [])

  async function create(event: FormEvent) {
    event.preventDefault(); setError(''); setBusy(true)
    try { const group = await api.createGroup(name); setGroups((items) => [...items, group]); setName('') }
    catch { setError('No se pudo crear el grupo.') }
    finally { setBusy(false) }
  }

  async function join(event: FormEvent) {
    event.preventDefault(); setError(''); setBusy(true)
    try { const group = await api.joinGroup(code); setGroups((items) => [...items.filter((item) => item.id !== group.id), group]); setCode('') }
    catch { setError('Código de invitación no válido.') }
    finally { setBusy(false) }
  }

  async function encourage(group: FriendGroup, userId: number) {
    setError(''); setBusy(true)
    try {
      const updated = await api.encourage(group.id, userId, '¡Sigue así! Vas muy bien.')
      setGroups((items) => items.map((item) => item.id === updated.id ? updated : item))
    } catch { setError('No se pudo enviar el ánimo.') }
    finally { setBusy(false) }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-5 sm:px-8 sm:py-8">
      <div className="flex items-start gap-3">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-leaf-soft text-leaf"><IconSparkle size={24} /></span>
        <div><h1 className="font-display text-2xl font-bold sm:text-3xl">Grupos privados</h1><p className="font-semibold text-ink-soft">Aprended juntos sin clasificaciones públicas.</p></div>
      </div>
      <div className="mt-7 grid gap-4 md:grid-cols-2">
        <form onSubmit={create} className="rounded-3xl bg-paper p-5 shadow-soft"><h2 className="font-display text-xl font-bold">Crear un grupo</h2><input required minLength={2} value={name} onChange={(event) => setName(event.target.value)} placeholder="Nombre del grupo" className="mt-4 w-full rounded-xl border border-ink/15 px-4 py-3" /><button disabled={busy} className="mt-3 w-full rounded-xl bg-terracotta px-5 py-2.5 font-bold text-paper disabled:opacity-50 sm:w-auto">Crear</button></form>
        <form onSubmit={join} className="rounded-3xl bg-paper p-5 shadow-soft"><h2 className="font-display text-xl font-bold">Unirse con código</h2><input required value={code} onChange={(event) => setCode(event.target.value)} placeholder="Código de invitación" className="mt-4 w-full rounded-xl border border-ink/15 px-4 py-3" /><button disabled={busy} className="mt-3 w-full rounded-xl bg-river px-5 py-2.5 font-bold text-paper disabled:opacity-50 sm:w-auto">Unirme</button></form>
      </div>
      {error && <p className="mt-4 font-semibold text-terracotta">{error}</p>}
      <div className="mt-6 grid gap-4">
        {groups.map((group) => (
          <section key={group.id} className="rounded-3xl bg-paper p-5 shadow-soft sm:p-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-between"><div><h2 className="font-display text-xl font-bold">{group.name}</h2><p className="mt-1 text-sm font-semibold text-ink-soft">{group.members.length} miembros</p></div><div className="self-start rounded-xl bg-sun-soft px-4 py-2 text-center"><p className="text-xs font-bold text-ink-soft">Código</p><p className="font-mono font-bold">{group.invite_code}</p></div></div>
            <div className="mt-4 flex flex-wrap gap-2">{group.members.filter((member) => member.user_id !== me?.id).map((member) => <button key={member.user_id} disabled={busy} onClick={() => void encourage(group, member.user_id)} className="rounded-full bg-leaf-soft px-3 py-1 text-sm font-semibold text-leaf disabled:opacity-50">Animar a {member.display_name}</button>)}</div>
            {group.encouragements.length > 0 && <div className="mt-4 border-t border-ink/8 pt-3"><p className="text-sm font-bold">Ánimos recientes</p>{group.encouragements.slice(0, 3).map((note) => <p key={note.id} className="mt-1 text-sm font-semibold text-ink-soft"><span className="font-bold text-ink">{note.from_display_name}:</span> {note.message}</p>)}</div>}
          </section>
        ))}
      </div>
    </div>
  )
}
