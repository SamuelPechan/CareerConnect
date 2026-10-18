import { type FormEvent, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type ContactCreate, type DiscoverySearch } from '../lib/api'

type FindContactsPageProps = { opportunityId: string; onNavigate: (path: string) => void }

export default function FindContactsPage({ opportunityId, onNavigate }: FindContactsPageProps) {
  const { token } = useAuth()
  const [search, setSearch] = useState<DiscoverySearch | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
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
        relationship_reason: current.relationship_reason || nextSearch.relationship_categories[0] || '',
      }))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to generate a contact search plan.')
    } finally {
      setIsLoading(false)
    }
  }

  const saveContact = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token || !search) return
    try {
      await api.createContact(token, {
        ...contactForm,
        job_title: contactForm.job_title || undefined,
        school: contactForm.school || undefined,
        profile_url: contactForm.profile_url || undefined,
        email: contactForm.email || undefined,
        notes: contactForm.notes || undefined,
        company_id: search.company_id || undefined,
        opportunity_id: opportunityId,
      })
      setSuccess(`${contactForm.name} was saved to your contacts.`)
      setContactForm((current) => ({ ...current, name: '', job_title: '', profile_url: '', email: '', notes: '' }))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save this contact.')
      setSuccess(null)
    }
  }

  const markReviewed = async (linkId: string, reviewed: boolean) => {
    if (!token || !search) return
    try {
      const updated = await api.reviewDiscoveryLink(token, linkId, reviewed)
      setSearch({ ...search, links: search.links.map((link) => link.id === updated.id ? updated : link) })
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to update this search link.')
    }
  }

  const criteria = search?.criteria ?? {}
  const listValue = (key: string) => Array.isArray(criteria[key]) ? (criteria[key] as string[]).join(', ') : String(criteria[key] ?? 'Not added')

  return (
    <main className="dashboard-shell">
      <nav className="topbar"><button className="brand brand-button" onClick={() => onNavigate('/applications')}>CareerConnect</button><button className="text-button" onClick={() => onNavigate('/applications')}>Back to opportunities</button></nav>
      <section className="page-content discovery-page">
        <div className="page-heading"><div><p className="eyebrow">Find contacts</p><h1>Build a thoughtful networking search.</h1><p className="muted">CareerConnect prepares search criteria and external links. You choose where to look, review public information yourself, and decide whether to reach out.</p></div></div>
        {error && <p className="error-message" role="alert">{error}</p>}
        {success && <p className="success-message" role="status">{success}</p>}
        {!search ? <section className="panel discovery-start"><h2>Ready to search?</h2><p className="muted">We’ll use this opportunity and your profile details to suggest useful relationship angles such as alumni, shared skills, and recruiting connections.</p><button className="primary-button" onClick={() => void generatePlan()} disabled={isLoading}>{isLoading ? 'Generating plan…' : 'Generate search plan'}</button></section> : <>
          <section className="panel"><div className="section-heading"><div><p className="eyebrow">Search context</p><h2>{String(criteria.job_title)} at {String(criteria.company_name)}</h2></div><button className="secondary-button" onClick={() => void generatePlan()} disabled={isLoading}>{isLoading ? 'Refreshing…' : 'Refresh plan'}</button></div><div className="criteria-grid"><div className="criteria-card"><span>School</span><strong>{listValue('school')}</strong></div><div className="criteria-card"><span>Major</span><strong>{listValue('major')}</strong></div><div className="criteria-card"><span>Skills</span><strong>{listValue('skills')}</strong></div><div className="criteria-card"><span>Previous employers</span><strong>{listValue('previous_employers')}</strong></div><div className="criteria-card"><span>Career interests</span><strong>{listValue('career_interests')}</strong></div><div className="criteria-card"><span>Location</span><strong>{listValue('location')}</strong></div></div></section>
          <section className="panel"><p className="eyebrow">Relationship angles</p><div className="tag-list">{search.relationship_categories.map((category) => <span className="tag" key={category}>{category}</span>)}</div><p className="instructions">{search.instructions}</p></section>
          <section><div className="section-heading"><div><p className="eyebrow">External search links</p><h2>Review each source yourself</h2></div><span className="count-badge">{search.links.filter((link) => link.reviewed).length}/{search.links.length} reviewed</span></div><div className="discovery-link-list">{search.links.map((link) => <article className="panel discovery-link-card" key={link.id}><div><h3>{link.platform}</h3><p className="muted">{link.relationship_reason}</p><small className="muted">Suggested query: {link.query}</small></div><div className="discovery-link-actions"><a className="primary-button" href={link.search_url} target="_blank" rel="noreferrer">Open search ↗</a><button className="secondary-button" onClick={() => void markReviewed(link.id, !link.reviewed)}>{link.reviewed ? 'Reviewed' : 'Mark reviewed'}</button></div></article>)}</div></section>
          <section className="panel contact-confirmation"><p className="eyebrow">Save a reviewed contact</p><h2>Confirm someone you found</h2><p className="muted">Enter only information you reviewed and are permitted to save. CareerConnect will not contact them automatically.</p><form className="opportunity-form" onSubmit={saveContact}><div className="form-grid"><label>Name<input required value={contactForm.name} onChange={(event) => setContactForm({ ...contactForm, name: event.target.value })} placeholder="Alex Johnson" /></label><label>Job title<input value={contactForm.job_title ?? ''} onChange={(event) => setContactForm({ ...contactForm, job_title: event.target.value })} placeholder="University Recruiter" /></label><label>Company<input required value={contactForm.company_name} onChange={(event) => setContactForm({ ...contactForm, company_name: event.target.value })} /></label><label>School<input value={contactForm.school ?? ''} onChange={(event) => setContactForm({ ...contactForm, school: event.target.value })} placeholder="Your university or theirs" /></label><label>Source platform<select value={contactForm.source_platform} onChange={(event) => setContactForm({ ...contactForm, source_platform: event.target.value })}><option>LinkedIn</option><option>Handshake</option><option>Company website</option><option>Alumni directory</option><option>Professional organization</option><option>Other</option></select></label><label>Relationship reason<select required value={contactForm.relationship_reason} onChange={(event) => setContactForm({ ...contactForm, relationship_reason: event.target.value })}>{search.relationship_categories.map((category) => <option key={category}>{category}</option>)}<option>Other relevant connection</option></select></label></div><div className="form-grid"><label>Profile URL<input type="url" value={contactForm.profile_url ?? ''} onChange={(event) => setContactForm({ ...contactForm, profile_url: event.target.value })} placeholder="https://…" /></label><label>Email, if permitted<input type="email" value={contactForm.email ?? ''} onChange={(event) => setContactForm({ ...contactForm, email: event.target.value })} placeholder="name@example.com" /></label></div><label>Notes<textarea value={contactForm.notes ?? ''} onChange={(event) => setContactForm({ ...contactForm, notes: event.target.value })} placeholder="What did you confirm about this relationship?" /></label><button className="primary-button" type="submit">Save contact</button></form></section>
        </>}
      </section>
    </main>
  )
}
