import { Navigate, Route, Routes } from 'react-router-dom'
import AuthView from './views/AuthView'
import AdminView from './views/AdminView'
import SubmitterView from './views/SubmitterView'

function App() {
  return (
    <Routes>
      <Route path="/" element={<AuthView />} />
      <Route path="/admin" element={<AdminView />} />
      <Route path="/admin/addcards" element={<AdminView />} />
      <Route path="/submitter" element={<SubmitterView />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App

