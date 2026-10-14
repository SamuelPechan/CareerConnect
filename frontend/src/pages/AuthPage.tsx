import { FormEvent, useState } from 'react'

import { useAuth } from '../auth/AuthContext'

type AuthPageProps = { mode: 'login' | 'register'; onNavigate: (path: string) => void }

export default function AuthPage({ mode, onNavigate }: AuthPageProps) {
  const { login, register, error } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFormError(null)
    setIsSubmitting(true)
    try {
      if (mode === 'login') await login(email, password)
      else await register(email, password)
    } catch (caught) {
      setFormError(caught instanceof Error ? caught.message : 'Please check your information.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const isRegister = mode === 'register'
  return (
    <main className="auth-shell">
      <section className="auth-card">
        <p className="eyebrow">CareerConnect</p>
        <h1>{isRegister ? 'Build your networking advantage.' : 'Welcome back.'}</h1>
        <p className="muted">
          {isRegister ? 'Create a private workspace for your applications, contacts, and follow-ups.' : 'Pick up where you left off with your job-search relationships.'}
        </p>
        <form onSubmit={handleSubmit} className="stack-form">
          <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" /></label>
          <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required minLength={8} autoComplete={isRegister ? 'new-password' : 'current-password'} /></label>
          <p className="form-hint">Use at least 8 characters.</p>
          {(formError || error) && <p className="error-message" role="alert">{formError || error}</p>}
          <button className="primary-button" disabled={isSubmitting}>{isSubmitting ? 'Please wait…' : isRegister ? 'Create account' : 'Log in'}</button>
        </form>
        <p className="switch-copy">
          {isRegister ? 'Already have an account?' : 'New to CareerConnect?'}{' '}
          <button className="text-button" onClick={() => onNavigate(isRegister ? '/login' : '/register')}>
            {isRegister ? 'Log in' : 'Create an account'}
          </button>
        </p>
      </section>
    </main>
  )
}
