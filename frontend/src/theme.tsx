import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'

type Theme = 'light' | 'dark'

const ThemeContext = createContext<{ theme: Theme; toggle: () => void } | null>(null)
const STORAGE_KEY = 'vamos.theme'

function initialTheme(): Theme {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(initialTheme)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    document.documentElement.style.colorScheme = theme
    localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, toggle: () => setTheme((value) => value === 'dark' ? 'light' : 'dark') }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function ThemeToggle({ compact = false }: { compact?: boolean }) {
  const context = useContext(ThemeContext)
  if (!context) return null
  const dark = context.theme === 'dark'
  return (
    <button type="button" onClick={context.toggle} aria-label={dark ? 'Usar modo claro' : 'Usar modo oscuro'} title={dark ? 'Modo claro' : 'Modo oscuro'} className="flex items-center justify-center gap-2 rounded-xl border border-ink/15 bg-paper px-3 py-2 text-sm font-bold text-ink shadow-soft transition hover:border-terracotta">
      <span aria-hidden="true">{dark ? '☀️' : '🌙'}</span>
      {!compact && <span>{dark ? 'Modo claro' : 'Modo oscuro'}</span>}
    </button>
  )
}
