import { NavLink, useNavigate } from 'react-router-dom'
import { setToken } from '../api/client'
import { IconBook, IconChart, IconChat, IconHome, IconRoute, IconSparkle } from './icons'
import { ThemeToggle } from '../theme'

const NAV = [
  { to: '/', label: 'Inicio', icon: IconHome, end: true },
  { to: '/ruta', label: 'Mi ruta', icon: IconRoute, end: false },
  { to: '/lecciones', label: 'Lecciones', icon: IconBook, end: false },
  { to: '/practica', label: 'Práctica', icon: IconChat, end: false },
  { to: '/progreso', label: 'Progreso', icon: IconChart, end: false },
  { to: '/grupos', label: 'Grupos', icon: IconSparkle, end: false },
]

function Logo({ dark }: { dark?: boolean }) {
  return (
    <div className={`font-display text-[26px] font-bold tracking-tight ${dark ? 'text-paper' : 'text-ink'}`}>
      ¡Vamos<span className="text-terracotta">!</span>
    </div>
  )
}

export function Sidebar({ dark = false }: { dark?: boolean }) {
  const navigate = useNavigate()
  return (
    <>
    <aside
      className={`hidden w-[190px] shrink-0 flex-col px-5 py-6 md:flex ${
        dark ? 'bg-navy text-paper' : 'border-r border-ink/8 bg-paper'
      }`}
    >
      <Logo dark={dark} />
      <nav className="mt-10 flex flex-col gap-1.5">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-[15px] font-semibold transition-colors ${
                isActive
                  ? dark
                    ? 'bg-terracotta text-paper'
                    : 'bg-blush text-terracotta'
                  : dark
                    ? 'text-paper/70 hover:bg-white/8 hover:text-paper'
                    : 'text-ink-soft hover:bg-cream-deep hover:text-ink'
              }`
            }
          >
            <item.icon size={19} />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto"><ThemeToggle /></div>
      <NavLink to="/perfil" className={`rounded-xl px-3 py-2 text-left text-sm font-bold ${dark ? 'text-paper/80 hover:bg-white/8' : 'text-terracotta hover:bg-blush'}`}>Mi nombre y perfil</NavLink>
      <button onClick={() => { setToken(null); navigate('/entrar') }} className={`rounded-xl px-3 py-2 text-left text-sm font-bold ${dark ? 'text-paper/70' : 'text-ink-soft'}`}>Cerrar sesión</button>
      {dark && (
        <div className="mt-4 overflow-hidden rounded-2xl">
          <div className="h-44 bg-[linear-gradient(160deg,#3d2b1f_0%,#7a4a2b_45%,#c78d54_75%,#2b1d14_100%)]">
            <div className="flex h-full items-end p-3">
              <span className="text-[11px] font-semibold text-paper/80">Charla con vecinos · A2</span>
            </div>
          </div>
        </div>
      )}
    </aside>
    <nav className={`fixed inset-x-0 bottom-0 z-50 grid grid-cols-6 border-t px-1 pb-[max(.35rem,env(safe-area-inset-bottom))] pt-1.5 md:hidden ${dark ? 'border-white/10 bg-navy' : 'border-ink/10 bg-paper'}`}>
      {NAV.map((item) => (
        <NavLink key={item.to} to={item.to} end={item.end} className={({ isActive }) => `flex min-w-0 flex-col items-center gap-0.5 rounded-lg py-1 text-[10px] font-bold ${isActive ? 'text-terracotta' : dark ? 'text-paper/65' : 'text-ink-soft'}`}>
          <item.icon size={20} />
          <span className="truncate">{item.label}</span>
        </NavLink>
      ))}
    </nav>
    </>
  )
}
