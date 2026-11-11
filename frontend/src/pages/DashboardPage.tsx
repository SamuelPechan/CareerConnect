import { useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type DashboardSummary, type Opportunity } from '../lib/api'

type DashboardPageProps = { onNavigate: (path: string) => void }

export default function DashboardPage({ onNavigate }: DashboardPageProps) {
  const { user, profile, token, logout } = useAuth()
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    Promise.all([
      api.getDashboardSummary(token),
      api.listOpportunities(token, new URLSearchParams({ sort_by: 'date_saved', sort_order: 'desc' })),
    ]).then(([nextSummary, nextOpportunities]) => {
      setSummary(nextSummary)
      setOpportunities(nextOpportunities.slice(0, 3))
    }).catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : 'Unable to load your workspace.')
    })
  }, [token])

  return (
    <main className="dashboard-shell">
      <nav className="topbar">
        <button className="brand brand-button" onClick={() => onNavigate('/')}>CareerConnect</button>
        <div className="nav-actions">
          <button className="text-button" onClick={() => onNavigate('/applications')}>Jobs</button>
          <button className="text-button" onClick={() => onNavigate('/networking')}>Contacts</button>
          <button className="text-button" onClick={() => void logout()}>Log out</button>
        </div>
      </nav>
      <section className="dashboard-content workspace-home">
        <p className="eyebrow">Your workspace</p>
        <h1>Turn a job into a focused outreach plan.</h1>
        <p className="muted">Welcome{profile?.major ? `, ${profile.major} student` : ''}. CareerConnect imports a job, finds public-web recommendations, prepares a thoughtful message, and keeps track of what happens next.</p>
        {error && <p className="error-message" role="alert">{error}</p>}
        <section className="workflow-steps" aria-label="CareerConnect workflow">
          <article className="workflow-step"><span>1</span><div><strong>Add a job</strong><p>Paste the role details you want to explore.</p></div></article>
          <article className="workflow-step"><span>2</span><div><strong>Review recommendations</strong><p>See a short public-web list with evidence and a reason for each suggestion.</p></div></article>
          <article className="workflow-step"><span>3</span><div><strong>Reach out carefully</strong><p>Edit every draft yourself, then record the follow-up.</p></div></article>
        </section>
        <section className="dashboard-callout panel"><div><p className="eyebrow">Recommended next step</p><h2>Start with a job posting.</h2><p className="muted">Paste one public job URL and let CareerConnect prepare a focused list of people to review.</p></div><button className="primary-button" onClick={() => onNavigate('/applications')}>Import a job</button></section>
        <section className="workspace-summary">
          <article className="metric-card"><span>Saved jobs</span><strong>{summary?.total_saved_opportunities ?? '—'}</strong><small>Roles in your workspace</small></article>
          <article className="metric-card"><span>People saved</span><strong>{summary?.total_contacts ?? '—'}</strong><small>Reviewed relationship candidates</small></article>
          <article className="metric-card"><span>Follow-ups</span><strong>{summary?.upcoming_follow_ups ?? '—'}</strong><small>Upcoming reminders</small></article>
        </section>
        <section>
          <div className="section-heading"><div><p className="eyebrow">Recent work</p><h2>Saved jobs</h2></div>{opportunities.length > 0 && <button className="text-button" onClick={() => onNavigate('/applications')}>View all</button>}</div>
          {opportunities.length === 0 ? <div className="empty-state panel"><h3>No jobs yet</h3><p className="muted">Import a role to start building a focused outreach plan.</p></div> : <div className="opportunity-list">{opportunities.map((opportunity) => <article className="opportunity-card" key={opportunity.id}><span className="card-status">{opportunity.status.replaceAll('_', ' ')}</span><strong>{opportunity.title}</strong><span>{opportunity.company_name}</span><div className="card-actions"><button className="secondary-button" onClick={() => onNavigate(`/recommendations/${opportunity.id}`)}>Find recommendations</button></div></article>)}</div>}
        </section>
        <p className="privacy-note"><strong>Safety promise:</strong> CareerConnect uses public professional sources only, never logs in to external platforms or sends messages, and never uses sensitive traits for recommendations. You approve every saved person and every message.</p>
        <p className="muted signed-in-note">Signed in as {user?.email}.</p>
      </section>
    </main>
  )
}
