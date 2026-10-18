import { type FormEvent, useEffect, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api, type Application, type Contact, type Interaction, type Reminder } from '../lib/api'

type NetworkingPageProps = { onNavigate: (path: string) => void }

export default function NetworkingPage({ onNavigate }: NetworkingPageProps) {
  const { token } = useAuth()
  const [contacts, setContacts] = useState<Contact[]>([])
  const [applications, setApplications] = useState<Application[]>([])
  const [selected, setSelected] = useState<Contact | null>(null)
  const [interactions, setInteractions] = useState<Interaction[]>([])
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [applicationId, setApplicationId] = useState('')
  const [interactionForm, setInteractionForm] = useState({ interaction_type: 'LinkedIn message', notes: '', outcome: '', next_steps: '' })
  const [reminderForm, setReminderForm] = useState({ title: '', due_at: '', notes: '' })
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const loadContacts = async () => {
    if (!token) return
    try {
      const [nextContacts, nextApplications] = await Promise.all([api.listContacts(token), api.listApplications(token)])
      setContacts(nextContacts)
      setApplications(nextApplications)
      setSelected((current) => current ? nextContacts.find((contact) => contact.id === current.id) ?? null : nextContacts[0] ?? null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to load networking data.')
    }
  }

  // Refresh the server-backed contact list when the authenticated session is ready.
  // eslint-disable-next-line react-hooks/set-state-in-effect, react-hooks/exhaustive-deps
  useEffect(() => { void loadContacts() }, [token])

  useEffect(() => {
    if (!token || !selected) return
    Promise.all([
      api.listInteractions(token, selected.id),
      api.listReminders(token, new URLSearchParams({ contact_id: selected.id })),
    ]).then(([nextInteractions, nextReminders]) => {
      setInteractions(nextInteractions)
      setReminders(nextReminders)
    }).catch((caught: unknown) => setError(caught instanceof Error ? caught.message : 'Unable to load contact activity.'))
  }, [token, selected])

  const submitInteraction = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token || !selected) return
    try {
      const created = await api.createInteraction(token, selected.id, {
        ...interactionForm,
        notes: interactionForm.notes || undefined,
        outcome: interactionForm.outcome || undefined,
        next_steps: interactionForm.next_steps || undefined,
      })
      setInteractions((current) => [created, ...current])
      setInteractionForm({ interaction_type: 'LinkedIn message', notes: '', outcome: '', next_steps: '' })
      setSuccess('Interaction recorded.')
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to record this interaction.')
    }
  }

  const submitReminder = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token || !selected) return
    try {
      const created = await api.createReminder(token, {
        title: reminderForm.title,
        due_at: reminderForm.due_at,
        notes: reminderForm.notes || undefined,
        contact_id: selected.id,
      })
      setReminders((current) => [...current, created].sort((left, right) => left.due_at.localeCompare(right.due_at)))
      setReminderForm({ title: '', due_at: '', notes: '' })
      setSuccess('Follow-up reminder created.')
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to create this reminder.')
    }
  }

  const connectToApplication = async () => {
    if (!token || !selected || !applicationId) return
    try {
      await api.connectContact(token, selected.id, applicationId)
      setSuccess('Contact connected to the application.')
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to connect this contact.')
    }
  }

  const toggleReminder = async (reminder: Reminder) => {
    if (!token) return
    try {
      const updated = await api.updateReminder(token, reminder.id, { completed: !reminder.completed })
      setReminders((current) => current.map((item) => item.id === updated.id ? updated : item))
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to update this reminder.')
    }
  }

  return (
    <main className="dashboard-shell">
      <nav className="topbar"><button className="brand brand-button" onClick={() => onNavigate('/')}>CareerConnect</button><div className="nav-actions"><button className="text-button" onClick={() => onNavigate('/')}>Dashboard</button><button className="text-button" onClick={() => onNavigate('/applications')}>Applications</button></div></nav>
      <section className="page-content">
        <div className="page-heading"><div><p className="eyebrow">Networking</p><h1>Build relationships around your applications.</h1><p className="muted">Keep contacts, conversations, application connections, and next steps together.</p></div><button className="primary-button" onClick={() => onNavigate('/applications')}>Find more contacts</button></div>
        {error && <p className="error-message" role="alert">{error}</p>}
        {success && <p className="success-message" role="status">{success}</p>}
        {selected && <button className="secondary-button full-button" onClick={() => onNavigate(`/message-drafts/${selected.id}`)}>Draft a message for {selected.name}</button>}
        <div className="applications-layout networking-layout"><section><div className="section-heading"><h2>Contacts</h2><span className="count-badge">{contacts.length}</span></div>{contacts.length === 0 ? <div className="empty-state panel"><h3>No saved contacts yet</h3><p className="muted">Review a Find Contacts result and save your first relationship.</p><button className="secondary-button" onClick={() => onNavigate('/applications')}>Open opportunities</button></div> : <div className="opportunity-list">{contacts.map((contact) => <button className={`opportunity-card ${selected?.id === contact.id ? 'selected' : ''}`} key={contact.id} onClick={() => setSelected(contact)}><span className="card-status">{contact.relationship_status}</span><strong>{contact.name}</strong><span>{contact.job_title || 'Role not added'} · {contact.company_name}</span><small>{contact.relationship_reason}</small></button>)}</div>}</section>
          <aside className="detail-panel panel">{selected ? <><div className="section-heading"><div><p className="eyebrow">Contact detail</p><h2>{selected.name}</h2></div><span className="count-badge">{selected.source_platform}</span></div><p className="detail-company">{selected.job_title || 'Role not added'} · {selected.company_name}</p><dl className="detail-list"><dt>School</dt><dd>{selected.school || 'Not added'}</dd><dt>Reason</dt><dd>{selected.relationship_reason}</dd><dt>Status</dt><dd>{selected.relationship_status}</dd></dl>{selected.profile_url && <a className="external-link" href={selected.profile_url} target="_blank" rel="noreferrer">Open profile ↗</a>}<section className="activity-block"><h3>Connect to application</h3><div className="inline-form"><select value={applicationId} onChange={(event) => setApplicationId(event.target.value)}><option value="">Choose an application</option>{applications.map((application) => <option key={application.id} value={application.id}>{application.opportunity.title} · {application.opportunity.company_name}</option>)}</select><button className="secondary-button" onClick={() => void connectToApplication()} disabled={!applicationId}>Connect</button></div></section><section className="activity-block"><h3>Record interaction</h3><form className="opportunity-form" onSubmit={submitInteraction}><label>Type<select value={interactionForm.interaction_type} onChange={(event) => setInteractionForm({ ...interactionForm, interaction_type: event.target.value })}><option>LinkedIn message</option><option>Email</option><option>Phone call</option><option>Informational interview</option><option>Career fair</option><option>Referral</option><option>Other</option></select></label><label>Notes<textarea required value={interactionForm.notes} onChange={(event) => setInteractionForm({ ...interactionForm, notes: event.target.value })} placeholder="What did you discuss?" /></label><label>Outcome<textarea value={interactionForm.outcome} onChange={(event) => setInteractionForm({ ...interactionForm, outcome: event.target.value })} placeholder="What happened?" /></label><label>Next steps<textarea value={interactionForm.next_steps} onChange={(event) => setInteractionForm({ ...interactionForm, next_steps: event.target.value })} placeholder="What should happen next?" /></label><button className="primary-button" type="submit">Record interaction</button></form></section><section className="activity-block"><h3>Schedule follow-up</h3><form className="opportunity-form" onSubmit={submitReminder}><label>Reminder title<input required value={reminderForm.title} onChange={(event) => setReminderForm({ ...reminderForm, title: event.target.value })} placeholder="Follow up after informational interview" /></label><label>Due date and time<input required type="datetime-local" value={reminderForm.due_at} onChange={(event) => setReminderForm({ ...reminderForm, due_at: event.target.value })} /></label><label>Notes<textarea value={reminderForm.notes} onChange={(event) => setReminderForm({ ...reminderForm, notes: event.target.value })} placeholder="What do you want to remember?" /></label><button className="primary-button" type="submit">Create reminder</button></form></section><section className="activity-block"><h3>Follow-ups</h3>{reminders.length === 0 ? <p className="muted">No reminders for this contact.</p> : <div className="activity-list">{reminders.map((reminder) => <label className={`activity-item ${reminder.completed ? 'completed' : ''}`} key={reminder.id}><input type="checkbox" checked={reminder.completed} onChange={() => void toggleReminder(reminder)} /><span><strong>{reminder.title}</strong><small>{new Date(reminder.due_at).toLocaleString()}</small></span></label>)}</div>}</section><section className="activity-block"><h3>Interaction history</h3>{interactions.length === 0 ? <p className="muted">No interactions recorded yet.</p> : <div className="activity-list">{interactions.map((interaction) => <article className="activity-item" key={interaction.id}><span><strong>{interaction.interaction_type}</strong><small>{new Date(interaction.occurred_at).toLocaleDateString()} · {interaction.notes}</small></span></article>)}</div>}</section></> : <div className="empty-state"><h3>Select a contact</h3><p className="muted">Choose a contact to see relationship history and plan the next step.</p></div>}</aside>
        </div>
      </section>
    </main>
  )
}
