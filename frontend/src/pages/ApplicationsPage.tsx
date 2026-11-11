import { FormEvent, useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type Opportunity, type OpportunityImportPreview } from '../lib/api'

type ApplicationsPageProps = { onNavigate: (path: string) => void }

export default function ApplicationsPage({ onNavigate }: ApplicationsPageProps) {
  const { token } = useAuth()
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [jobUrl, setJobUrl] = useState('')
  const [preview, setPreview] = useState<OpportunityImportPreview | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isImporting, setIsImporting] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
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

  const importJob = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token || !jobUrl.trim()) return
    setIsImporting(true)
    try {
      setPreview(await api.previewOpportunityImport(token, jobUrl.trim()))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to read that job posting.')
      setPreview(null)
    } finally {
      setIsImporting(false)
    }
  }

  const saveImportedJob = async () => {
    if (!token || !preview) return
    setIsSaving(true)
    try {
      const created = await api.createOpportunity(token, {
        title: preview.title,
        company_name: preview.company_name,
        location: preview.location || undefined,
        job_url: preview.job_url,
        source_platform: preview.source_platform,
        description: preview.description || undefined,
      })
      setPreview(null)
      setJobUrl('')
      await loadOpportunities()
      onNavigate(`/recommendations/${created.id}`)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save the imported job.')
    } finally {
      setIsSaving(false)
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
            <p className="eyebrow">Start here</p>
            <h1>Bring in a job. Get a focused people list.</h1>
            <p className="muted">Paste one public job posting URL. CareerConnect reads only public job metadata, shows you what it found, and waits for your approval before saving it.</p>
          </div>
        </div>
        {error && <p className="error-message" role="alert">{error}</p>}
        <form onSubmit={importJob} className="opportunity-form panel quick-start-card">
          <div className="section-heading"><div><p className="eyebrow">One-step import</p><h2>Paste the job posting URL</h2></div></div>
          <label>Public job URL<input required type="url" value={jobUrl} onChange={(event) => setJobUrl(event.target.value)} placeholder="https://www.linkedin.com/jobs/view/..." /></label>
          <p className="privacy-note"><strong>Safety first:</strong> Use a public posting URL only. CareerConnect does not use your cookies, log in to job sites, or import private messages and resumes.</p>
          <button className="primary-button" disabled={isImporting}>{isImporting ? 'Reading public job details…' : 'Preview job'}</button>
        </form>
        {preview && <section className="panel import-preview-card"><div className="section-heading"><div><p className="eyebrow">Review before saving</p><h2>{preview.title}</h2><p className="muted">{preview.company_name}{preview.location ? ` · ${preview.location}` : ''} · {preview.source_platform}</p></div><button className="text-button" onClick={() => setPreview(null)}>Discard</button></div><p className="preview-description">{preview.description || 'No public description was available.'}</p><div className="card-actions"><button className="primary-button" onClick={() => void saveImportedJob()} disabled={isSaving}>{isSaving ? 'Saving job…' : 'Save and find recommendations'}</button><a className="text-button" href={preview.job_url} target="_blank" rel="noreferrer">Open original posting ↗</a></div></section>}
        <section>
          <div className="section-heading"><div><p className="eyebrow">Your workspace</p><h2>Saved jobs</h2></div><span className="count-badge">{opportunities.length}</span></div>
          {isLoading ? <p className="muted">Loading jobs…</p> : opportunities.length === 0 ? <div className="empty-state panel"><h3>No jobs yet</h3><p className="muted">Import one public posting above to start.</p></div> : <div className="opportunity-list">{opportunities.map((opportunity) => <article className="opportunity-card" key={opportunity.id}><span className="card-status">{opportunity.status.replaceAll('_', ' ')}</span><strong>{opportunity.title}</strong><span>{opportunity.company_name}{opportunity.location ? ` · ${opportunity.location}` : ''}</span><small>{opportunity.source_platform || 'Source not added'}</small><div className="card-actions"><button className="secondary-button" onClick={() => onNavigate(`/recommendations/${opportunity.id}`)}>Find recommendations</button>{opportunity.job_url && <a className="text-button" href={opportunity.job_url} target="_blank" rel="noreferrer">Open posting ↗</a>}</div></article>)}</div>}
        </section>
      </section>
    </main>
  )
}
