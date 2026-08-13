import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { getToken } from './api/client'
import { AppLayout } from './components/AppLayout'
import { Assessment } from './pages/Assessment'
import { Grupos } from './pages/Grupos'
import { Inicio } from './pages/Inicio'
import { MiRuta } from './pages/MiRuta'
import { Practica } from './pages/Practica'
import { Progreso } from './pages/Progreso'
import { Auth } from './pages/Auth'

function RequireAuth() {
  return getToken() ? <Outlet /> : <Navigate to="/entrar" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/entrar" element={<Auth />} />
        <Route element={<RequireAuth />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Inicio />} />
            <Route path="/ruta" element={<MiRuta />} />
            <Route path="/practica" element={<Practica />} />
            <Route path="/progreso" element={<Progreso />} />
            <Route path="/grupos" element={<Grupos />} />
          </Route>
          <Route element={<AppLayout dark />}>
            <Route path="/prueba" element={<Assessment />} />
            <Route path="/leccion/:lessonId/prueba" element={<Assessment />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
