import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { API_UNAVAILABLE_EVENT, getToken, placementComplete } from './api/client'
import { AppLayout } from './components/AppLayout'
import { Assessment } from './pages/Assessment'
import { Grupos } from './pages/Grupos'
import { Inicio } from './pages/Inicio'
import { MiRuta } from './pages/MiRuta'
import { Practica } from './pages/Practica'
import { Progreso } from './pages/Progreso'
import { Auth } from './pages/Auth'
import { Placement } from './pages/Placement'
import { Lecciones } from './pages/Lecciones'
import { Leccion } from './pages/Leccion'
import { Perfil } from './pages/Perfil'
import { Conversacion } from './pages/Conversacion'
import { Repaso } from './pages/Repaso'
import { VideoShadowing } from './pages/VideoShadowing'

function RequireAuth() {
  return getToken() ? <Outlet /> : <Navigate to="/entrar" replace />
}

function RequirePlacement() {
  return placementComplete() ? <Outlet /> : <Navigate to="/nivel" replace />
}

function ApiUnavailableBanner() {
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const show = () => setVisible(true)
    const hide = () => setVisible(false)
    window.addEventListener(API_UNAVAILABLE_EVENT, show)
    window.addEventListener('online', hide)
    return () => {
      window.removeEventListener(API_UNAVAILABLE_EVENT, show)
      window.removeEventListener('online', hide)
    }
  }, [])
  if (!visible) return null
  return <div role="alert" className="fixed inset-x-3 top-3 z-[100] rounded-2xl bg-terracotta p-4 text-center font-bold text-paper shadow-card">
    No podemos conectar con el servicio. Comprueba Internet y, si continúa, <a className="underline" href="https://github.com/Polarwin/Espanol/releases/latest" target="_blank" rel="noreferrer">actualiza la aplicación</a>.
  </div>
}

export default function App() {
  return (
    <BrowserRouter>
      <ApiUnavailableBanner />
      <Routes>
        <Route path="/entrar" element={<Auth />} />
        <Route element={<RequireAuth />}>
          <Route path="/nivel" element={<Placement />} />
          <Route element={<RequirePlacement />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Inicio />} />
            <Route path="/ruta" element={<MiRuta />} />
            <Route path="/lecciones" element={<Lecciones />} />
            <Route path="/leccion/:lessonId" element={<Leccion />} />
            <Route path="/leccion/:lessonId/repetir-video" element={<VideoShadowing />} />
            <Route path="/practica" element={<Practica />} />
            <Route path="/repaso" element={<Repaso />} />
            <Route path="/conversacion" element={<Conversacion />} />
            <Route path="/leccion/:lessonId/conversacion" element={<Conversacion />} />
            <Route path="/progreso" element={<Progreso />} />
            <Route path="/grupos" element={<Grupos />} />
            <Route path="/perfil" element={<Perfil />} />
          </Route>
          <Route element={<AppLayout dark />}>
            <Route path="/prueba" element={<Assessment />} />
            <Route path="/leccion/:lessonId/prueba" element={<Assessment />} />
          </Route>
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
