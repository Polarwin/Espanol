import { Link } from 'react-router-dom'
import { IconChat } from '../components/icons'

export function Practica() {
  return (
    <div className="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center px-8 text-center">
      <span className="flex h-16 w-16 items-center justify-center rounded-full bg-blush text-terracotta">
        <IconChat size={30} />
      </span>
      <h1 className="mt-5 font-display text-[32px] font-bold">Práctica</h1>
      <p className="mt-2 text-[15px] font-semibold text-ink-soft">
        Aquí podrás repasar vocabulario, gramática y pronunciación con repaso espaciado. Estamos
        preparándolo.
      </p>
      <Link
        to="/ruta"
        className="mt-6 rounded-full bg-terracotta px-6 py-2.5 text-sm font-bold text-paper shadow-soft transition hover:bg-terracotta-dark"
      >
        Volver a mi ruta
      </Link>
    </div>
  )
}
