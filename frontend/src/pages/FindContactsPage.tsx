import { useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type DiscoverySearch } from '../lib/api'

type FindContactsPageProps = { opportunityId: string; onNavigate: (path: string) => void }

export default function FindContactsPage({ opportunityId, onNavigate }: FindContactsPageProps) {
  const { token } = useAuth()
  const [search, setSearch] = useState<DiscoverySearch | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generatePlan = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      setSearch(await api.findContacts(token, opportunityId))
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to generate a contact search plan.')
    } finally {
      setIsLoading(false)
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
        {!search ? <section className="panel discovery-start"><h2>Ready to search?</h2><p className="muted">We’ll use this opportunity and your profile details to suggest useful relationship angles such as alumni, shared skills, and recruiting connections.</p><button className="primary-button" onClick={() => void generatePlan()} disabled={isLoading}>{isLoading ? 'Generating plan…' : 'Generate search plan'}</button></section> : <>
          <section className="panel"><div className="section-heading"><div><p className="eyebrow">Search context</p><h2>{String(criteria.job_title)} at {String(criteria.company_name)}</h2></div><button className="secondary-button" onClick={() => void generatePlan()} disabled={isLoading}>{isLoading ? 'Refreshing…' : 'Refresh plan'}</button></div><div className="criteria-grid"><div className="criteria-card"><span>School</span><strong>{listValue('school')}</strong></div><div className="criteria-card"><span>Major</span><strong>{listValue('major')}</strong></div><div className="criteria-card"><span>Skills</span><strong>{listValue('skills')}</strong></div><div className="criteria-card"><span>Previous employers</span><strong>{listValue('previous_employers')}</strong></div><div className="criteria-card"><span>Career interests</span><strong>{listValue('career_interests')}</strong></div><div className="criteria-card"><span>Location</span><strong>{listValue('location')}</strong></div></div></section>
          <section className="panel"><p className="eyebrow">Relationship angles</p><div className="tag-list">{search.relationship_categories.map((category) => <span className="tag" key={category}>{category}</span>)}</div><p className="instructions">{search.instructions}</p></section>
          <section><div className="section-heading"><div><p className="eyebrow">External search links</p><h2>Review each source yourself</h2></div><span className="count-badge">{search.links.filter((link) => link.reviewed).length}/{search.links.length} reviewed</span></div><div className="discovery-link-list">{search.links.map((link) => <article className="panel discovery-link-card" key={link.id}><div><h3>{link.platform}</h3><p className="muted">{link.relationship_reason}</p><small className="muted">Suggested query: {link.query}</small></div><div className="discovery-link-actions"><a className="primary-button" href={link.search_url} target="_blank" rel="noreferrer">Open search ↗</a><button className="secondary-button" onClick={() => void markReviewed(link.id, !link.reviewed)}>{link.reviewed ? 'Reviewed' : 'Mark reviewed'}</button></div></article>)}</div></section>
        </>}
      </section>
    </main>
  )
}
