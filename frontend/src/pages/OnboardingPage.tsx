import { FormEvent, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api } from '../lib/api'

type OnboardingPageProps = { onComplete: () => Promise<void> }
type FormState = { school: string; major: string; skills: string; career_interests: string }

const splitValues = (value: string) => value.split(',').map((item) => item.trim()).filter(Boolean)

export default function OnboardingPage({ onComplete }: OnboardingPageProps) {
  const { token, profile } = useAuth()
  const [form, setForm] = useState<FormState>({
    school: profile?.school ?? '',
    major: profile?.major ?? '',
    skills: profile?.skills.join(', ') ?? '',
    career_interests: profile?.career_interests.join(', ') ?? '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const setField = (field: keyof FormState, value: string) => {
    setForm((current) => ({ ...current, [field]: value }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token) return
    setError(null)
    setIsSubmitting(true)
    try {
      await api.updateProfile(token, {
        school: form.school.trim() || null,
        major: form.major.trim() || null,
        skills: splitValues(form.skills),
        career_interests: splitValues(form.career_interests),
        previous_employers: [],
        locations: [],
        preferred_job_types: [],
        preferred_industries: [],
        onboarding_completed: true,
      })
      await onComplete()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save your profile.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="onboarding-shell">
      <section className="onboarding-card">
        <div className="step-label">Your workspace · 1 of 1</div>
        <h1>Give recommendations a little context.</h1>
        <p className="muted">These optional details help CareerConnect suggest more relevant relationship angles for a job. You can change them later.</p>
        <form onSubmit={handleSubmit} className="stack-form">
          <div className="form-grid">
            <label>School<input value={form.school} onChange={(event) => setField('school', event.target.value)} placeholder="University or college" /></label>
            <label>Major or field<input value={form.major} onChange={(event) => setField('major', event.target.value)} placeholder="Computer science" /></label>
          </div>
          <label>Skills <span className="label-hint">comma separated</span><input value={form.skills} onChange={(event) => setField('skills', event.target.value)} placeholder="Python, research, project management" /></label>
          <label>Career interests <span className="label-hint">comma separated</span><input value={form.career_interests} onChange={(event) => setField('career_interests', event.target.value)} placeholder="Product, healthcare, fintech" /></label>
          <p className="privacy-note"><strong>Privacy note:</strong> CareerConnect does not connect to outside accounts or send messages automatically. Only add information you are comfortable storing.</p>
          {error && <p className="error-message" role="alert">{error}</p>}
          <button className="primary-button" disabled={isSubmitting}>{isSubmitting ? 'Saving profile…' : 'Continue to CareerConnect'}</button>
        </form>
      </section>
    </main>
  )
}
