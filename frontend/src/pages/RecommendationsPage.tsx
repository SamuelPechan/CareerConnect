import { useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type Opportunity, type Recommendation } from '../lib/api'

type RecommendationsPageProps = { opportunityId: string; onNavigate: (path: string) => void }

export default function RecommendationsPage({ opportunityId, onNavigate }: RecommendationsPageProps) {
  const { token } = useAuth()
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [providerNote, setProviderNote] = useState('')
  const [consent, setConsent] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSearching, setIsSearching] = useState(false)
  const [savingName, setSavingName] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    api.getOpportunity(token, opportunityId).then(setOpportunity).catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : 'Unable to load this job.')
    }).finally(() => setIsLoading(false))
  }, [token, opportunityId])

  const findRecommendations = async () => {
    if (!token || !consent) return
    setIsSearching(true)
    try {
      const result = await api.recommendConnections(token, opportunityId)
      setRecommendations(result.recommendations)
      setProviderNote(result.provider_note)
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to find recommendations.')
    } finally {
      setIsSearching(false)
    }
  }

  const saveAndDraft = async (recommendation: Recommendation) => {
    if (!token || !opportunity) return
    setSavingName(recommendation.name)
    try {
      const contact = await api.createContact(token, {
        name: recommendation.name,
        job_title: recommendation.job_title,
        company_name: recommendation.company_name,
        relationship_reason: recommendation.connection_reason,
        source_platform: 'Public web research',
        profile_url: recommendation.profile_url,
        notes: `${recommendation.evidence} Evidence: ${recommendation.source_title} — ${recommendation.source_url}`,
        opportunity_id: opportunity.id,
        company_id: opportunity.company_id || undefined,
      })
      onNavigate(`/message-drafts/${contact.id}`)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save this recommendation.')
    } finally {
      setSavingName(null)
    }
  }

  if (isLoading) return <main className="shell"><p>Loading recommendation context…</p></main>

  return (
    <main className="dashboard-shell">
      <nav className="topbar"><button className="brand brand-button" onClick={() => onNavigate('/')}>CareerConnect</button><div className="nav-actions"><button className="text-button" onClick={() => onNavigate('/applications')}>Jobs</button><button className="text-button" onClick={() => onNavigate('/networking')}>Contacts</button></div></nav>
      <section className="page-content assistant-page">
        <div className="page-heading"><div><p className="eyebrow">Career assistant</p><h1>Find people worth reaching out to.</h1><p className="muted">CareerConnect searches public professional sources and returns a short, evidence-backed list. It does not access your external accounts or send outreach.</p></div></div>
        {error && <p className="error-message" role="alert">{error}</p>}
        {opportunity && <section className="panel assistant-start"><p className="eyebrow">Job context</p><h2>{opportunity.title}</h2><p className="muted">{opportunity.company_name}{opportunity.location ? ` · ${opportunity.location}` : ''}</p><p className="privacy-note"><strong>Privacy and cost check:</strong> To find recommendations, CareerConnect sends this job’s public details and limited professional context from your profile—school, major, skills, interests, industries, and locations—to the configured AI search provider. It does not send your email, password, resume, private notes, or sensitive traits.</p><label className="consent-row"><input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} />I understand and want CareerConnect to search public professional sources.</label><button className="primary-button" onClick={() => void findRecommendations()} disabled={!consent || isSearching}>{isSearching ? 'Searching public sources…' : 'Find recommendations'}</button></section>}
        {recommendations.length > 0 && <section><div className="section-heading"><div><p className="eyebrow">Review results</p><h2>Potential connections</h2></div><span className="count-badge">{recommendations.length}</span></div><p className="muted">{providerNote}</p><div className="recommendation-list">{recommendations.map((recommendation) => <article className="panel recommendation-card" key={`${recommendation.name}-${recommendation.source_url}`}><div className="recommendation-heading"><div><span className={`confidence-badge confidence-${recommendation.confidence}`}>{recommendation.confidence} confidence</span><h2>{recommendation.name}</h2><p className="muted">{recommendation.job_title} · {recommendation.company_name}</p></div></div><div className="recommendation-copy"><p><strong>Why this could help:</strong> {recommendation.connection_reason}</p><p><strong>Public evidence:</strong> {recommendation.evidence}</p></div><div className="recommendation-links"><a className="text-button" href={recommendation.profile_url} target="_blank" rel="noreferrer">Review profile ↗</a><a className="text-button" href={recommendation.source_url} target="_blank" rel="noreferrer">{recommendation.source_title} ↗</a></div><div className="card-actions"><button className="primary-button" onClick={() => void saveAndDraft(recommendation)} disabled={savingName !== null}>{savingName === recommendation.name ? 'Saving…' : 'Save and draft message'}</button><span className="label-hint">Saving is your approval. Review the source first.</span></div></article>)}</div></section>}
        {recommendations.length === 0 && !isSearching && <section className="panel empty-state assistant-empty"><h2>No recommendations yet</h2><p className="muted">Check the consent box and run the public-web search when you are ready.</p></section>}
      </section>
    </main>
  )
}
