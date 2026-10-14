import { FormEvent, useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type Opportunity, type OpportunityCreate } from '../lib/api'

type ApplicationsPageProps = { onNavigate: (path: string) => void }

const emptyForm: OpportunityCreate = { title: '', company_name: '', location: '', job_url: '', source_platform: '', notes: '' }

export default function ApplicationsPage({ onNavigate }: ApplicationsPageProps) {
  const { token } = useAuth()
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [selected, setSelected] = useState<Opportunity | null>(null)
  const [form, setForm] = useState<OpportunityCreate>(emptyForm)
  const [companyFilter, setCompanyFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [sourceFilter, setSourceFilter] = useState('')
  const [isAdding, setIsAdding] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadOpportunities = async () => {
    if (!token) return
    setIsLoading(true)
    const params = new URLSearchParams({ sort_by: 'date_saved', sort_order: 'desc' })
    if (companyFilter) params.set('company', companyFilter)
    if (statusFilter) params.set('status', statusFilter)
    if (sourceFilter) params.set('source_platform', sourceFilter)
    try {
      setOpportunities(await api.listOpportunities(token, params))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load opportunities.')
    } finally {
      setIsLoading(false)
    }
  }

  // This effect intentionally refreshes server-backed data when the filters change.
  // eslint-disable-next-line react-hooks/set-state-in-effect, react-hooks/exhaustive-deps
  useEffect(() => { void loadOpportunities() }, [token, companyFilter, statusFilter, sourceFilter])

  const createOpportunity = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token) return
    try {
      const created = await api.createOpportunity(token, form)
      setForm(emptyForm)
      setIsAdding(false)
      setSelected(created)
      await loadOpportunities()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save this opportunity.')
    }
  }

  const applyNow = async (opportunity: Opportunity) => {
    if (!token) return
    try {
      await api.applyToOpportunity(token, opportunity.id)
      await loadOpportunities()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to convert this opportunity.')
    }
  }

  const updateApplicationStatus = async (opportunity: Opportunity, nextStatus: string) => {
    if (!token || !opportunity.application) return
    try {
      const updated = await api.updateApplication(token, opportunity.application.id, { status: nextStatus })
      setOpportunities((current) => current.map((item) => item.id === opportunity.id ? updated.opportunity : item))
      setSelected(updated.opportunity)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to update application status.')
    }
  }

  const deleteOpportunity = async (opportunity: Opportunity) => {
    if (!token) return
    try {
      await api.deleteOpportunity(token, opportunity.id)
      setSelected(null)
      await loadOpportunities()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to delete this opportunity.')
    }
  }

  return (
    <main className="dashboard-shell">
      <nav className="topbar"><button className="brand brand-button" onClick={() => onNavigate('/')}>CareerConnect</button><button className="text-button" onClick={() => onNavigate('/')}>Dashboard</button></nav>
      <section className="page-content">
        <div className="page-heading"><div><p className="eyebrow">Applications</p><h1>Keep every opportunity in view.</h1><p className="muted">Save roles now, convert them into applications when you apply, and keep status changes in one place.</p></div><button className="primary-button" onClick={() => setIsAdding((current) => !current)}>{isAdding ? 'Close form' : 'Add opportunity'}</button></div>
        {isAdding && <form onSubmit={createOpportunity} className="opportunity-form panel"><h2>Add a job opportunity</h2><div className="form-grid"><label>Job title<input required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} placeholder="Software Engineering Intern" /></label><label>Company<input required value={form.company_name} onChange={(event) => setForm({ ...form, company_name: event.target.value })} placeholder="Company name" /></label><label>Location<input value={form.location} onChange={(event) => setForm({ ...form, location: event.target.value })} placeholder="New York, NY or Remote" /></label><label>Source platform<input value={form.source_platform} onChange={(event) => setForm({ ...form, source_platform: event.target.value })} placeholder="LinkedIn, Handshake, company site" /></label></div><label>Job URL<input type="url" value={form.job_url} onChange={(event) => setForm({ ...form, job_url: event.target.value })} placeholder="https://…" /></label><label>Notes<textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} placeholder="Why is this role interesting?" /></label><button className="primary-button">Save opportunity</button></form>}
        <div className="filter-bar panel"><input aria-label="Filter by company" value={companyFilter} onChange={(event) => setCompanyFilter(event.target.value)} placeholder="Search company" /><select aria-label="Filter by status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="">All opportunity statuses</option><option value="saved">Saved</option><option value="planning_to_apply">Planning to apply</option></select><input aria-label="Filter by source" value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value)} placeholder="Filter source" /></div>
        {error && <p className="error-message" role="alert">{error}</p>}
        <div className="applications-layout"><section><div className="section-heading"><h2>Opportunities</h2><span className="count-badge">{opportunities.length}</span></div>{isLoading ? <p className="muted">Loading opportunities…</p> : opportunities.length === 0 ? <div className="empty-state panel"><h3>No opportunities yet</h3><p className="muted">Save your first role to start building a networking plan around it.</p></div> : <div className="opportunity-list">{opportunities.map((opportunity) => <button className={`opportunity-card ${selected?.id === opportunity.id ? 'selected' : ''}`} key={opportunity.id} onClick={() => setSelected(opportunity)}><span className="card-status">{opportunity.application?.status ?? opportunity.status.replaceAll('_', ' ')}</span><strong>{opportunity.title}</strong><span>{opportunity.company_name}{opportunity.location ? ` · ${opportunity.location}` : ''}</span><small>{opportunity.source_platform || 'Source not added'}</small></button>)}</div>}</section><aside className="detail-panel panel">{selected ? <><div className="section-heading"><div><p className="eyebrow">Opportunity detail</p><h2>{selected.title}</h2></div><button className="text-button danger-button" onClick={() => void deleteOpportunity(selected)}>Delete</button></div><p className="detail-company">{selected.company_name}{selected.location ? ` · ${selected.location}` : ''}</p><dl className="detail-list"><dt>Status</dt><dd>{selected.application?.status ?? selected.status.replaceAll('_', ' ')}</dd><dt>Source</dt><dd>{selected.source_platform || 'Not added'}</dd><dt>Saved</dt><dd>{new Date(selected.date_saved).toLocaleDateString()}</dd></dl>{selected.job_url && <a className="external-link" href={selected.job_url} target="_blank" rel="noreferrer">Open job posting ↗</a>}<button className="secondary-button full-button" onClick={() => onNavigate(`/find-contacts/${selected.id}`)}>Find contacts</button>{selected.application ? <label className="status-control">Application status<select value={selected.application.status} onChange={(event) => void updateApplicationStatus(selected, event.target.value)}><option value="applied">Applied</option><option value="interviewing">Interviewing</option><option value="rejected">Rejected</option><option value="offer">Offer</option><option value="withdrawn">Withdrawn</option></select></label> : <button className="primary-button full-button" onClick={() => void applyNow(selected)}>Convert to application</button>}<div className="detail-note"><strong>Notes</strong><p>{selected.notes || 'No notes yet.'}</p></div></> : <div className="empty-state"><h3>Select an opportunity</h3><p className="muted">Review its details here, then convert it into an application when you apply.</p></div>}</aside></div>
      </section>
    </main>
  )
}
