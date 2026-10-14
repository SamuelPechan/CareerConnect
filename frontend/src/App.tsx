import { useEffect, useState } from 'react'

import { AuthProvider, useAuth } from './auth/AuthContext'
import AuthPage from './pages/AuthPage'
import ApplicationsPage from './pages/ApplicationsPage'
import DashboardPage from './pages/DashboardPage'
import FindContactsPage from './pages/FindContactsPage'
import OnboardingPage from './pages/OnboardingPage'

function AppContent() {
  const { user, profile, isLoading, refreshProfile } = useAuth()
  const [path, setPath] = useState(window.location.pathname)

  useEffect(() => {
    const handlePopState = () => setPath(window.location.pathname)
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const navigate = (nextPath: string) => {
    window.history.pushState({}, '', nextPath)
    setPath(nextPath)
  }

  if (isLoading) return <main className="shell"><p>Loading your workspace…</p></main>
  if (!user) return <AuthPage mode={path === '/register' ? 'register' : 'login'} onNavigate={navigate} />
  if (!profile?.onboarding_completed) return <OnboardingPage onComplete={refreshProfile} />
  if (path.startsWith('/find-contacts/')) {
    return <FindContactsPage opportunityId={path.split('/')[2]} onNavigate={navigate} />
  }
  if (path === '/applications') return <ApplicationsPage onNavigate={navigate} />
  return <DashboardPage onNavigate={navigate} />
}

function App() {
  return <AuthProvider><AppContent /></AuthProvider>
}

export default App
