import { Link, Outlet, useNavigate } from 'react-router-dom'
import { setToken } from '../api/client'
import { Sidebar } from './Sidebar'

export function AppLayout({ dark = false }: { dark?: boolean }) {
  const navigate = useNavigate()
  return (
    <div className="flex min-h-screen bg-cream">
      <Sidebar dark={dark} />
      <div className={`fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b px-4 md:hidden ${dark ? 'border-white/10 bg-navy text-paper' : 'border-ink/8 bg-paper text-ink'}`}>
        <span className="font-display text-xl font-bold">¡Vamos<span className="text-terracotta">!</span></span>
        <div className="flex items-center gap-4"><Link to="/perfil" className="text-sm font-bold text-terracotta">Mi perfil</Link><button onClick={() => { setToken(null); navigate('/entrar') }} className="text-sm font-bold text-ink-soft">Salir</button></div>
      </div>
      <main className="min-w-0 flex-1 pb-20 pt-14 md:pb-0 md:pt-0">
        <Outlet />
      </main>
    </div>
  )
}
