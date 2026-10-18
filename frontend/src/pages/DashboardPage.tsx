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

  const pipeline = summary?.applications_by_status ?? {}
  const pipelineTotal = Math.max(...Object.values(pipeline), 1)

  return (
    <main className="dashboard-shell">
      <nav className="topbar"><button className="brand brand-button" onClick={() => onNavigate('/')}>CareerConnect</button><div className="nav-actions"><button className="text-button" onClick={() => onNavigate('/applications')}>Applications</button><button className="text-button" onClick={() => onNavigate('/networking')}>Networking</button><button className="text-button" onClick={() => void logout()}>Log out</button></div></nav>
      <section className="dashboard-content">
        <p className="eyebrow">Your workspace</p>
        <h1>Build momentum through people.</h1>
        <p className="muted">You’re signed in as {user?.email}. Save opportunities, track applications, and build the networking context around each role.</p>
        {error && <p className="error-message" role="alert">{error}</p>}
        <div className="dashboard-grid">
          <article className="metric-card"><span>Profile</span><strong>Complete</strong><small>{profile?.school || 'School not added'}</small></article>
          <article className="metric-card"><span>Opportunities</span><strong>{summary?.total_saved_opportunities ?? '—'}</strong><small>Roles in your workspace</small></article>
          <article className="metric-card"><span>Applications</span><strong>{summary?.total_applications ?? '—'}</strong><small>{summary?.total_interviews ?? 0} interviewing · {summary?.total_offers ?? 0} offers</small></article>
          <article className="metric-card"><span>Contacts</span><strong>{summary?.total_contacts ?? '—'}</strong><small>{summary?.upcoming_follow_ups ?? 0} upcoming follow-ups</small></article>
        </div>
        <div className="analytics-grid">
          <article className="metric-card"><span>Networking coverage</span><strong>{summary?.applications_with_contacts ?? '—'} / {summary?.total_applications ?? '—'}</strong><small>Applications connected to contacts</small></article>
          <article className="metric-card"><span>Discovery activity</span><strong>{summary?.reviewed_discovery_links ?? '—'} / {summary?.total_discovery_links ?? '—'}</strong><small>Search links reviewed</small></article>
          <article className="metric-card"><span>Follow-up health</span><strong>{summary?.overdue_follow_ups ?? '—'} overdue</strong><small>{summary?.upcoming_follow_ups ?? 0} upcoming · {summary?.total_interactions ?? 0} interactions</small></article>
        </div>
        <div className="analytics-columns">
          <section className="panel analytics-panel"><div className="section-heading"><div><p className="eyebrow">Application pipeline</p><h2>Status distribution</h2></div></div>{Object.keys(pipeline).length === 0 ? <p className="muted">Your application statuses will appear here as you track roles.</p> : <div className="pipeline-list">{Object.entries(pipeline).map(([status, count]) => <div className="pipeline-row" key={status}><div className="pipeline-label"><span>{status.replaceAll('_', ' ')}</span><strong>{count}</strong></div><div className="pipeline-track"><span style={{ width: `${(count / pipelineTotal) * 100}%` }} /></div></div>)}</div>}</section>
          <section className="panel analytics-panel"><p className="eyebrow">Networking signals</p><h2>Keep context attached to outcomes.</h2><div className="rate-grid"><div><strong>{summary?.interview_rate == null ? '—' : `${summary.interview_rate}%`}</strong><span>Interview rate</span></div><div><strong>{summary?.offer_rate == null ? '—' : `${summary.offer_rate}%`}</strong><span>Offer rate</span></div></div><p className="muted">{summary?.applications_without_contacts ?? 0} applications still have no connected contact. Use Networking to add context and plan the next follow-up.</p><button className="secondary-button" onClick={() => onNavigate('/networking')}>Review networking</button></section>
        </div>
        <section className="dashboard-callout panel"><div><p className="eyebrow">Next action</p><h2>Keep your pipeline moving.</h2><p className="muted">Add a role you’re considering, then connect conversations and follow-ups around it.</p></div><div className="nav-actions"><button className="secondary-button" onClick={() => onNavigate('/networking')}>Open networking</button><button className="primary-button" onClick={() => onNavigate('/applications')}>Open applications</button></div></section>
      </section>
    </main>
  )
}
