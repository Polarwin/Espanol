import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'

export function AppLayout({ dark = false }: { dark?: boolean }) {
  return (
    <div className="flex min-h-screen bg-cream">
      <Sidebar dark={dark} />
      <main className="min-w-0 flex-1">
        <Outlet />
      </main>
    </div>
  )
}
