import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { getToken, placementComplete } from './api/client'
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

function RequireAuth() {
  return getToken() ? <Outlet /> : <Navigate to="/entrar" replace />
}

function RequirePlacement() {
  return placementComplete() ? <Outlet /> : <Navigate to="/nivel" replace />
}

export default function App() {
  return (
    <BrowserRouter>
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
