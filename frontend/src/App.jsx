import { Navigate, Route, Routes } from 'react-router-dom'
import AuthView from './views/AuthView'
import AdminView from './views/AdminView'
import SubmitView from './views/SubmitView'

function App() {
  return (
    <Routes>
      <Route path="/" element={<AuthView />} />
      <Route path="/login" element={<AuthView />} />

      <Route path="/admin" element={<AdminView />} />
      <Route path="/admin/cards" element={<AdminView />} />

      <Route path="/submit" element={<SubmitView />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}



export default App

