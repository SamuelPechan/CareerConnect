import { FormEvent, useState } from 'react'

import { api } from '../lib/api'

type ForgotPasswordPageProps = { onNavigate: (path: string) => void }

export default function ForgotPasswordPage({ onNavigate }: ForgotPasswordPageProps) {
  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [resetLink, setResetLink] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)
    setError(null)
    setMessage(null)
    setResetLink(null)
    try {
      const response = await api.requestPasswordReset(email)
      setMessage(response.message)
      if (response.reset_token) {
        setResetLink(`${window.location.origin}/reset-password?token=${encodeURIComponent(response.reset_token)}`)
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to request a password reset.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <p className="eyebrow">CareerConnect</p>
        <h1>Reset your password.</h1>
        <p className="muted">Enter your account email and we’ll help you get back into your workspace.</p>
        <form onSubmit={handleSubmit} className="stack-form">
          <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" /></label>
          {error && <p className="error-message" role="alert">{error}</p>}
          {message && <p className="success-message" role="status">{message}</p>}
          {resetLink && (
            <div className="reset-link-card">
              <strong>Development reset link</strong>
              <a href={resetLink}>Continue to choose a new password</a>
              <small>This link is shown here because email delivery is not configured yet.</small>
            </div>
          )}
          <button className="primary-button" disabled={isSubmitting}>{isSubmitting ? 'Creating reset link…' : 'Reset password'}</button>
        </form>
        <p className="switch-copy"><button className="text-button" onClick={() => onNavigate('/login')}>Back to log in</button></p>
      </section>
    </main>
  )
}
