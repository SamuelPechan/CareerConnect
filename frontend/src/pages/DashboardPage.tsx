import { useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type DashboardSummary } from '../lib/api'

type DashboardPageProps = { onNavigate: (path: string) => void }

export default function DashboardPage({ onNavigate }: DashboardPageProps) {
  const { user, profile, token, logout } = useAuth()
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    api.getDashboardSummary(token).then(setSummary).catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : 'Unable to load dashboard statistics.')
    })
  }, [token])

  return (
    <main className="dashboard-shell">
      <nav className="topbar"><button className="brand brand-button" onClick={() => onNavigate('/')}>CareerConnect</button><div className="nav-actions"><button className="text-button" onClick={() => onNavigate('/applications')}>Applications</button><button className="text-button" onClick={() => void logout()}>Log out</button></div></nav>
      <section className="dashboard-content">
        <p className="eyebrow">Your workspace</p>
        <h1>Build momentum through people.</h1>
        <p className="muted">You’re signed in as {user?.email}. Save opportunities, track applications, and build the networking context around each role.</p>
        {error && <p className="error-message" role="alert">{error}</p>}
        <div className="dashboard-grid">
          <article className="metric-card"><span>Profile</span><strong>Complete</strong><small>{profile?.school || 'School not added'}</small></article>
          <article className="metric-card"><span>Opportunities</span><strong>{summary?.total_saved_opportunities ?? '—'}</strong><small>Roles in your workspace</small></article>
          <article className="metric-card"><span>Applications</span><strong>{summary?.total_applications ?? '—'}</strong><small>{summary?.total_interviews ?? 0} interviewing · {summary?.total_offers ?? 0} offers</small></article>
        </div>
        <section className="dashboard-callout panel"><div><p className="eyebrow">Next action</p><h2>Keep your pipeline moving.</h2><p className="muted">Add a role you’re considering, then convert it into an application when you apply.</p></div><button className="primary-button" onClick={() => onNavigate('/applications')}>Open applications</button></section>
      </section>
    </main>
  )
}
