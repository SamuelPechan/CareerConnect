import { FormEvent, useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type Contact, type ContactCreate, type DiscoverySearch } from '../lib/api'

type FindContactsPageProps = { opportunityId: string; onNavigate: (path: string) => void }

export default function FindContactsPage({ opportunityId, onNavigate }: FindContactsPageProps) {
  const { token } = useAuth()
  const [search, setSearch] = useState<DiscoverySearch | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [savedContact, setSavedContact] = useState<Contact | null>(null)
  const [contactForm, setContactForm] = useState<ContactCreate>({
    name: '', company_name: '', relationship_reason: '', source_platform: 'LinkedIn',
  })

  const generatePlan = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      const nextSearch = await api.findContacts(token, opportunityId)
      setSearch(nextSearch)
      setContactForm((current) => ({
        ...current,
        company_name: String(nextSearch.criteria.company_name ?? current.company_name),
        relationship_reason: current.relationship_reason || nextSearch.relationship_categories[0] || 'Relevant professional connection',
      }))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to generate search angles.')
    } finally {
      setIsLoading(false)
    }
  }

  // The plan is generated once when the user enters this job's workflow.
  // eslint-disable-next-line react-hooks/set-state-in-effect, react-hooks/exhaustive-deps
  useEffect(() => { void generatePlan() }, [token, opportunityId])

  const saveContact = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token || !search) return
    setIsSaving(true)
    try {
      const created = await api.createContact(token, {
        ...contactForm,
        name: contactForm.name.trim(),
        company_name: contactForm.company_name.trim(),
        job_title: contactForm.job_title?.trim() || undefined,
        school: contactForm.school?.trim() || undefined,
        profile_url: contactForm.profile_url?.trim() || undefined,
        notes: contactForm.notes?.trim() || undefined,
        company_id: search.company_id || undefined,
        opportunity_id: opportunityId,
      })
      setSavedContact(created)
      setSuccess(`${created.name} was saved after your review.`)
      setContactForm((current) => ({ ...current, name: '', job_title: '', school: '', profile_url: '', notes: '' }))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save this person.')
      setSuccess(null)
    } finally {
      setIsSaving(false)
    }
  }

  const markReviewed = async (linkId: string, reviewed: boolean) => {
    if (!token || !search) return
    try {
      const updated = await api.reviewDiscoveryLink(token, linkId, reviewed)
      setSearch({ ...search, links: search.links.map((link) => link.id === updated.id ? updated : link) })
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to update this search record.')
    }
  }

  const criteria = search?.criteria ?? {}
  const listValue = (key: string) => Array.isArray(criteria[key]) ? (criteria[key] as string[]).join(', ') : String(criteria[key] ?? 'Not added')

  if (isLoading && !search) return <main className="shell"><p>Preparing safe search angles…</p></main>

  return (
    <main className="dashboard-shell">
      <nav className="topbar">
        <button className="brand brand-button" onClick={() => onNavigate('/')}>CareerConnect</button>
        <div className="nav-actions"><button className="text-button" onClick={() => onNavigate('/applications')}>Back to jobs</button><button className="text-button" onClick={() => onNavigate('/networking')}>Contacts</button></div>
      </nav>
      <section className="page-content discovery-page">
        <div className="page-heading"><div><p className="eyebrow">Step 2 · Review people</p><h1>Find relevant people, with you in control.</h1><p className="muted">CareerConnect creates search angles from the job and your profile. It does not access external accounts or claim that a person is a match until you review them.</p></div></div>
        {error && <p className="error-message" role="alert">{error}</p>}
        {success && <p className="success-message" role="status">{success}</p>}
        {search && <>
          <section className="panel"><div className="section-heading"><div><p className="eyebrow">Search context</p><h2>{String(criteria.job_title)} at {String(criteria.company_name)}</h2></div><button className="secondary-button" onClick={() => void generatePlan()} disabled={isLoading}>{isLoading ? 'Refreshing…' : 'Refresh angles'}</button></div><div className="criteria-grid"><div className="criteria-card"><span>School</span><strong>{listValue('school')}</strong></div><div className="criteria-card"><span>Major</span><strong>{listValue('major')}</strong></div><div className="criteria-card"><span>Skills</span><strong>{listValue('skills')}</strong></div><div className="criteria-card"><span>Career interests</span><strong>{listValue('career_interests')}</strong></div><div className="criteria-card"><span>Location</span><strong>{listValue('location')}</strong></div></div></section>
          <section className="panel"><p className="eyebrow">Relationship angles</p><div className="tag-list">{search.relationship_categories.map((category) => <span className="tag" key={category}>{category}</span>)}</div><p className="instructions">{search.instructions}</p></section>
          <section><div className="section-heading"><div><p className="eyebrow">External sources</p><h2>Search and review public information</h2></div><span className="count-badge">{search.links.filter((link) => link.reviewed).length}/{search.links.length} reviewed</span></div><div className="discovery-link-list">{search.links.map((link) => <article className="panel discovery-link-card" key={link.id}><div><h3>{link.platform}</h3><p className="muted">{link.relationship_reason}</p><small className="muted">Suggested query: {link.query}</small></div><div className="discovery-link-actions"><a className="primary-button" href={link.search_url} target="_blank" rel="noreferrer">Open search ↗</a><button className="secondary-button" onClick={() => void markReviewed(link.id, !link.reviewed)}>{link.reviewed ? 'Reviewed' : 'Mark reviewed'}</button></div></article>)}</div></section>
          <section className="panel contact-confirmation"><p className="eyebrow">Save only after review</p><h2>Add a person you found</h2><p className="muted">Use information you reviewed and are permitted to store. Do not add private contact details, sensitive traits, or information copied from a restricted source.</p><form className="opportunity-form" onSubmit={saveContact}><div className="form-grid"><label>Name<input required value={contactForm.name} onChange={(event) => setContactForm({ ...contactForm, name: event.target.value })} placeholder="Alex Johnson" /></label><label>Job title <span className="label-hint">optional</span><input value={contactForm.job_title ?? ''} onChange={(event) => setContactForm({ ...contactForm, job_title: event.target.value })} placeholder="University Recruiter" /></label><label>Company<input required value={contactForm.company_name} onChange={(event) => setContactForm({ ...contactForm, company_name: event.target.value })} /></label><label>School or community <span className="label-hint">optional</span><input value={contactForm.school ?? ''} onChange={(event) => setContactForm({ ...contactForm, school: event.target.value })} placeholder="Shared school or organization" /></label><label>Source platform<select value={contactForm.source_platform} onChange={(event) => setContactForm({ ...contactForm, source_platform: event.target.value })}><option>LinkedIn</option><option>Handshake</option><option>Company website</option><option>Alumni directory</option><option>Professional organization</option><option>Other</option></select></label><label>Why relevant<select required value={contactForm.relationship_reason} onChange={(event) => setContactForm({ ...contactForm, relationship_reason: event.target.value })}>{search.relationship_categories.map((category) => <option key={category}>{category}</option>)}<option>Other relevant connection</option></select></label></div><label>Public profile URL <span className="label-hint">optional</span><input type="url" value={contactForm.profile_url ?? ''} onChange={(event) => setContactForm({ ...contactForm, profile_url: event.target.value })} placeholder="https://…" /></label><label>Review note <span className="label-hint">optional</span><textarea value={contactForm.notes ?? ''} onChange={(event) => setContactForm({ ...contactForm, notes: event.target.value })} placeholder="What did you confirm about this relationship?" /></label><button className="primary-button" type="submit" disabled={isSaving}>{isSaving ? 'Saving…' : 'Save reviewed person'}</button></form></section>
          {savedContact && <section className="panel next-action-card"><div><p className="eyebrow">Next step</p><h2>Prepare a careful message for {savedContact.name}.</h2><p className="muted">The draft is only a starting point. You must review, edit, copy, and send it yourself.</p></div><button className="primary-button" onClick={() => onNavigate(`/message-drafts/${savedContact.id}`)}>Draft a message</button></section>}
        </>}
      </section>
    </main>
  )
}
