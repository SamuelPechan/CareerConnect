import { useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type Application, type Contact, type MessageDraft } from '../lib/api'

type MessageDraftPageProps = { contactId: string; onNavigate: (path: string) => void }

export default function MessageDraftPage({ contactId, onNavigate }: MessageDraftPageProps) {
  const { token } = useAuth()
  const [contact, setContact] = useState<Contact | null>(null)
  const [applications, setApplications] = useState<Application[]>([])
  const [draft, setDraft] = useState<MessageDraft | null>(null)
  const [messageType, setMessageType] = useState('linkedin')
  const [opportunityId, setOpportunityId] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    Promise.all([api.getContact(token, contactId), api.listApplications(token)]).then(([nextContact, nextApplications]) => {
      setContact(nextContact)
      setApplications(nextApplications)
      setOpportunityId(nextContact.opportunity_id || '')
    }).catch((caught: unknown) => setError(caught instanceof Error ? caught.message : 'Unable to load message context.')).finally(() => setIsLoading(false))
  }, [token, contactId])

  const generateDraft = async () => {
    if (!token) return
    try {
      const generated = await api.generateMessageDraft(token, { contact_id: contactId, opportunity_id: opportunityId || undefined, message_type: messageType })
      setDraft(generated)
      setSuccess('Draft generated. Review and edit it before using it.')
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to generate this draft.')
    }
  }

  const saveDraft = async (status?: string) => {
    if (!token || !draft) return
    try {
      const updated = await api.updateMessageDraft(token, draft.id, { subject: draft.subject ?? '', body: draft.body, status })
      setDraft(updated)
      setSuccess(status === 'approved' ? 'Draft approved for your manual use.' : 'Draft changes saved.')
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save this draft.')
    }
  }

  const copyDraft = async () => {
    if (!draft || !token) return
    try {
      await navigator.clipboard.writeText(draft.body)
      const updated = await api.updateMessageDraft(token, draft.id, { status: 'copied' })
      setDraft(updated)
      setSuccess('Draft copied. Review it again when pasting it into the external platform.')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to copy this draft.')
    }
  }

  if (isLoading) return <main className="shell"><p>Loading message context…</p></main>

  return (
    <main className="dashboard-shell">
      <nav className="topbar"><button className="brand brand-button" onClick={() => onNavigate('/networking')}>CareerConnect</button><button className="text-button" onClick={() => onNavigate('/networking')}>Back to networking</button></nav>
      <section className="page-content draft-page">
        <div className="page-heading"><div><p className="eyebrow">Message drafts</p><h1>Write with context. Send with care.</h1><p className="muted">CareerConnect can assemble a starting point from your saved relationship context. You must review, edit, copy, and send every message yourself.</p></div></div>
        {error && <p className="error-message" role="alert">{error}</p>}
        {success && <p className="success-message" role="status">{success}</p>}
        {contact && <section className="panel draft-context"><p className="eyebrow">Recipient</p><h2>{contact.name}</h2><p className="muted">{contact.job_title || 'Role not added'} · {contact.company_name} · {contact.relationship_reason}</p><div className="form-grid"><label>Message type<select value={messageType} onChange={(event) => setMessageType(event.target.value)}><option value="linkedin">LinkedIn connection/message</option><option value="email">Email</option><option value="informational_interview">Informational interview request</option><option value="thank_you">Thank-you note</option></select></label><label>Related application<select value={opportunityId} onChange={(event) => setOpportunityId(event.target.value)}><option value="">Use contact context only</option>{applications.map((application) => <option key={application.opportunity.id} value={application.opportunity.id}>{application.opportunity.title} · {application.opportunity.company_name}</option>)}</select></label></div><button className="primary-button" onClick={() => void generateDraft()}>{draft ? 'Generate new draft' : 'Generate draft'}</button></section>}
        {draft && <section className="panel draft-editor"><div className="section-heading"><div><p className="eyebrow">{draft.status}</p><h2>Review your draft</h2></div><span className="count-badge">Manual review required</span></div><label>Subject<input value={draft.subject ?? ''} onChange={(event) => setDraft({ ...draft, subject: event.target.value })} placeholder="Optional for LinkedIn messages" /></label><label className="draft-body-label">Message<textarea className="draft-body" value={draft.body} onChange={(event) => setDraft({ ...draft, body: event.target.value })} /></label><div className="draft-actions"><button className="secondary-button" onClick={() => void saveDraft()}>Save edits</button><button className="secondary-button" onClick={() => void saveDraft('approved')}>Approve draft</button><button className="primary-button" onClick={() => void copyDraft()}>Copy to clipboard</button>{draft.status !== 'sent' && <button className="text-button" onClick={() => void saveDraft('sent')}>Mark sent manually</button>}<button className="text-button danger-button" onClick={() => void saveDraft('archived')}>Archive</button></div></section>}
      </section>
    </main>
  )
}
