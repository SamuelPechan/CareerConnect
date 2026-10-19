import { FormEvent, useState } from 'react'

import { api } from '../lib/api'

type ResetPasswordPageProps = { onNavigate: (path: string) => void }

export default function ResetPasswordPage({ onNavigate }: ResetPasswordPageProps) {
  const token = new URLSearchParams(window.location.search).get('token') ?? ''
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(token ? null : 'This reset link is missing its token.')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    if (password !== confirmation) {
      setError('Passwords do not match.')
      return
    }
    setIsSubmitting(true)
    try {
      const response = await api.resetPassword(token, password)
      setMessage(response.message)
      setTimeout(() => onNavigate('/login'), 1200)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to reset your password.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <p className="eyebrow">CareerConnect</p>
        <h1>Choose a new password.</h1>
        <p className="muted">Use at least 8 characters, then log in with your new password.</p>
        <form onSubmit={handleSubmit} className="stack-form">
          <label>New password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required minLength={8} autoComplete="new-password" /></label>
          <label>Confirm password<input type="password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required minLength={8} autoComplete="new-password" /></label>
          {error && <p className="error-message" role="alert">{error}</p>}
          {message && <p className="success-message" role="status">{message}</p>}
          <button className="primary-button" disabled={isSubmitting || !token}>{isSubmitting ? 'Updating password…' : 'Update password'}</button>
        </form>
        <p className="switch-copy"><button className="text-button" onClick={() => onNavigate('/login')}>Back to log in</button></p>
      </section>
    </main>
  )
}
