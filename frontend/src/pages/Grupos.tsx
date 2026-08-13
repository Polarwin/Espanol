import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api/client'
import type { FriendGroup } from '../api/types'
import { IconSparkle } from '../components/icons'

export function Grupos() {
  const [groups, setGroups] = useState<FriendGroup[]>([])
  const [name, setName] = useState('')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  useEffect(() => { api.getGroups().then(setGroups).catch(() => setError('No se pudieron cargar tus grupos.')) }, [])

  async function create(event: FormEvent) {
    event.preventDefault(); setError('')
    try { const group = await api.createGroup(name); setGroups(g => [...g, group]); setName('') }
    catch { setError('No se pudo crear el grupo.') }
  }
  async function join(event: FormEvent) {
    event.preventDefault(); setError('')
    try { const group = await api.joinGroup(code); setGroups(g => [...g.filter(x => x.id !== group.id), group]); setCode('') }
    catch { setError('Código de invitación no válido.') }
  }

  return <div className="mx-auto max-w-4xl px-8 py-8">
    <div className="flex items-center gap-3"><span className="flex h-12 w-12 items-center justify-center rounded-full bg-leaf-soft text-leaf"><IconSparkle size={24} /></span><div><h1 className="font-display text-3xl font-bold">Grupos privados</h1><p className="font-semibold text-ink-soft">Aprended juntos sin clasificaciones públicas.</p></div></div>
    <div className="mt-7 grid gap-4 md:grid-cols-2">
      <form onSubmit={create} className="rounded-3xl bg-paper p-5 shadow-soft"><h2 className="font-display text-xl font-bold">Crear un grupo</h2><input required minLength={2} value={name} onChange={e => setName(e.target.value)} placeholder="Nombre del grupo" className="mt-4 w-full rounded-xl border border-ink/15 px-4 py-3"/><button className="mt-3 rounded-xl bg-terracotta px-5 py-2.5 font-bold text-paper">Crear</button></form>
      <form onSubmit={join} className="rounded-3xl bg-paper p-5 shadow-soft"><h2 className="font-display text-xl font-bold">Unirse con código</h2><input required value={code} onChange={e => setCode(e.target.value)} placeholder="Código de invitación" className="mt-4 w-full rounded-xl border border-ink/15 px-4 py-3"/><button className="mt-3 rounded-xl bg-river px-5 py-2.5 font-bold text-paper">Unirme</button></form>
    </div>
    {error && <p className="mt-4 font-semibold text-terracotta">{error}</p>}
    <div className="mt-6 grid gap-4">{groups.map(group => <section key={group.id} className="rounded-3xl bg-paper p-6 shadow-soft"><div className="flex justify-between gap-4"><div><h2 className="font-display text-xl font-bold">{group.name}</h2><p className="mt-1 text-sm font-semibold text-ink-soft">{group.members.length} miembros</p></div><div className="rounded-xl bg-sun-soft px-4 py-2 text-center"><p className="text-xs font-bold text-ink-soft">Código</p><p className="font-mono font-bold">{group.invite_code}</p></div></div><div className="mt-4 flex flex-wrap gap-2">{group.members.map(member => <span key={member.user_id} className="rounded-full bg-leaf-soft px-3 py-1 text-sm font-semibold text-leaf">{member.display_name}</span>)}</div></section>)}</div>
  </div>
}
