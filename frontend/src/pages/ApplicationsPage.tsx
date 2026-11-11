import { FormEvent, useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type Opportunity, type OpportunityCreate } from '../lib/api'

type ApplicationsPageProps = { onNavigate: (path: string) => void }

const emptyForm: OpportunityCreate = {
  title: '', company_name: '', job_url: '', source_platform: '', notes: '',
}

export default function ApplicationsPage({ onNavigate }: ApplicationsPageProps) {
  const { token } = useAuth()
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [form, setForm] = useState<OpportunityCreate>(emptyForm)
  const [isAdding, setIsAdding] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadOpportunities = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      setOpportunities(await api.listOpportunities(token, new URLSearchParams({ sort_by: 'date_saved', sort_order: 'desc' })))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load jobs.')
    } finally {
      setIsLoading(false)
    }
  }

  // Refresh server-backed data when the authenticated session is ready.
  // eslint-disable-next-line react-hooks/set-state-in-effect, react-hooks/exhaustive-deps
  useEffect(() => { void loadOpportunities() }, [token])

  const createOpportunity = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token) return
    setIsSubmitting(true)
    try {
      const created = await api.createOpportunity(token, {
        ...form,
        title: form.title.trim(),
        company_name: form.company_name.trim(),
        job_url: form.job_url?.trim() || undefined,
        source_platform: form.source_platform?.trim() || undefined,
        notes: form.notes?.trim() || undefined,
      })
      setForm(emptyForm)
      setIsAdding(false)
      setError(null)
      await loadOpportunities()
      onNavigate(`/find-contacts/${created.id}`)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save this job.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="dashboard-shell">
      <nav className="topbar">
        <button className="brand brand-button" onClick={() => onNavigate('/')}>CareerConnect</button>
        <div className="nav-actions">
          <button className="text-button" onClick={() => onNavigate('/')}>Workspace</button>
          <button className="text-button" onClick={() => onNavigate('/networking')}>Contacts</button>
        </div>
      </nav>
      <section className="page-content">
        <div className="page-heading">
          <div>
            <p className="eyebrow">Step 1 · Add a job</p>
            <h1>Start with one opportunity.</h1>
            <p className="muted">Save a role, then CareerConnect will build search angles for relevant people. You review every result yourself.</p>
          </div>
          {!isAdding && <button className="primary-button" onClick={() => setIsAdding(true)}>Add a job</button>}
        </div>
        {error && <p className="error-message" role="alert">{error}</p>}
        {isAdding && <form onSubmit={createOpportunity} className="opportunity-form panel quick-start-card">
          <div className="section-heading"><div><p className="eyebrow">Quick start</p><h2>What role are you exploring?</h2></div><button type="button" className="text-button" onClick={() => setIsAdding(false)}>Close</button></div>
          <div className="form-grid">
            <label>Job title<input required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} placeholder="Software Engineering Intern" /></label>
            <label>Company<input required value={form.company_name} onChange={(event) => setForm({ ...form, company_name: event.target.value })} placeholder="Company name" /></label>
          </div>
          <label>Job posting URL <span className="label-hint">optional; CareerConnect stores it but does not crawl or log in</span><input type="url" value={form.job_url} onChange={(event) => setForm({ ...form, job_url: event.target.value })} placeholder="https://…" /></label>
          <div className="form-grid">
            <label>Where did you find it? <span className="label-hint">optional</span><input value={form.source_platform} onChange={(event) => setForm({ ...form, source_platform: event.target.value })} placeholder="LinkedIn, Handshake, company site" /></label>
            <label>Private note <span className="label-hint">optional</span><input value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} placeholder="Why this role interests you" /></label>
          </div>
          <p className="privacy-note"><strong>Safety first:</strong> Do not paste passwords, private messages, or sensitive personal information into CareerConnect.</p>
          <button className="primary-button" disabled={isSubmitting}>{isSubmitting ? 'Saving job…' : 'Save and find relevant people'}</button>
        </form>}
        <section>
          <div className="section-heading"><div><p className="eyebrow">Your workspace</p><h2>Saved jobs</h2></div><span className="count-badge">{opportunities.length}</span></div>
          {isLoading ? <p className="muted">Loading jobs…</p> : opportunities.length === 0 ? <div className="empty-state panel"><h3>Your next step starts here</h3><p className="muted">Save a job above to generate safe, user-reviewed search angles.</p></div> : <div className="opportunity-list">{opportunities.map((opportunity) => <article className="opportunity-card" key={opportunity.id}><span className="card-status">{opportunity.status.replaceAll('_', ' ')}</span><strong>{opportunity.title}</strong><span>{opportunity.company_name}{opportunity.location ? ` · ${opportunity.location}` : ''}</span><small>{opportunity.source_platform || 'Source not added'}</small><div className="card-actions"><button className="secondary-button" onClick={() => onNavigate(`/find-contacts/${opportunity.id}`)}>Find relevant people</button>{opportunity.job_url && <a className="text-button" href={opportunity.job_url} target="_blank" rel="noreferrer">Open posting ↗</a>}</div></article>)}</div>}
        </section>
      </section>
    </main>
  )
}
