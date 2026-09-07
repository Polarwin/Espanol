import { NavLink, Outlet } from 'react-router-dom'
import { IconChat, IconSparkle } from './icons'

export function PracticeLayout() {
  return <>
    <div className="mx-auto max-w-3xl px-4 pt-6 sm:px-8">
      <h1 className="font-display text-3xl font-bold">Práctica</h1>
      <p className="mt-1 text-sm font-semibold text-ink-soft">Repasa con ejercicios o conversa con Ana.</p>
      <nav aria-label="Tipos de práctica" className="mt-4 flex gap-2 rounded-2xl bg-paper p-1.5 shadow-soft">
        {[
          { to: '/practica', label: 'Ejercicios', icon: IconChat, end: true },
          { to: '/practica/conversacion', label: 'Conversar', icon: IconSparkle, end: false },
        ].map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => `flex flex-1 items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-sm font-bold ${isActive ? 'bg-terracotta text-paper' : 'text-ink-soft hover:bg-cream'}`}><Icon size={18} />{label}</NavLink>)}
      </nav>
    </div>
    <Outlet />
  </>
}
