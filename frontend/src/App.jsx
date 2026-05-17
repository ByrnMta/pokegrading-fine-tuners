import { useState } from 'react'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'

function App() {
  const [view, setView] = useState('login')

  return (
    <div>
      {view === 'login' ? (
        <LoginForm onSwitch={(target) => setView(target)} />
      ) : (
        <RegisterForm onSwitch={(target) => setView(target)} />
      )}
    </div>
  )
}

export default App

