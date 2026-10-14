import { FormEvent, useState } from 'react'

import { useAuth } from '../auth/AuthContext'
import { api } from '../lib/api'

type OnboardingPageProps = { onComplete: () => Promise<void> }
type FormState = Record<string, string>

const initialForm: FormState = {
  school: '', major: '', graduation_year: '', skills: '', previous_employers: '',
  locations: '', career_interests: '', preferred_job_types: '', preferred_industries: '',
  resume_file_name: '', resume_url: '',
}

const splitValues = (value: string) => value.split(',').map((item) => item.trim()).filter(Boolean)

export default function OnboardingPage({ onComplete }: OnboardingPageProps) {
  const { token, profile } = useAuth()
  const [form, setForm] = useState<FormState>(() => ({
    ...initialForm,
    school: profile?.school ?? '', major: profile?.major ?? '',
    graduation_year: profile?.graduation_year?.toString() ?? '', skills: profile?.skills.join(', ') ?? '',
    previous_employers: profile?.previous_employers.join(', ') ?? '', locations: profile?.locations.join(', ') ?? '',
    career_interests: profile?.career_interests.join(', ') ?? '', preferred_job_types: profile?.preferred_job_types.join(', ') ?? '',
    preferred_industries: profile?.preferred_industries.join(', ') ?? '',
  }))
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const setField = (field: string, value: string) => setForm((current) => ({ ...current, [field]: value }))
  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!token) return
    setError(null)
    setIsSubmitting(true)
    try {
      await api.updateProfile(token, {
        school: form.school || null, major: form.major || null,
        graduation_year: form.graduation_year ? Number(form.graduation_year) : null,
        skills: splitValues(form.skills), previous_employers: splitValues(form.previous_employers),
        locations: splitValues(form.locations), career_interests: splitValues(form.career_interests),
        preferred_job_types: splitValues(form.preferred_job_types), preferred_industries: splitValues(form.preferred_industries),
        onboarding_completed: true,
      })
      if (form.resume_file_name.trim()) {
        await api.createResume(token, { file_name: form.resume_file_name.trim(), file_url: form.resume_url.trim() || undefined })
      }
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
        <h1>Let’s make your networking relevant.</h1>
        <p className="muted">Tell us what you are looking for. CareerConnect uses this information to shape job-specific contact discovery later.</p>
        <form onSubmit={handleSubmit} className="stack-form">
          <div className="form-grid">
            <label>School<input value={form.school} onChange={(event) => setField('school', event.target.value)} placeholder="University or college" /></label>
            <label>Major<input value={form.major} onChange={(event) => setField('major', event.target.value)} placeholder="Computer science" /></label>
            <label>Graduation year<input type="number" min="1950" max="2100" value={form.graduation_year} onChange={(event) => setField('graduation_year', event.target.value)} placeholder="2027" /></label>
            <label>Preferred locations<input value={form.locations} onChange={(event) => setField('locations', event.target.value)} placeholder="Seattle, Remote" /></label>
          </div>
          <label>Skills <span className="label-hint">comma separated</span><input value={form.skills} onChange={(event) => setField('skills', event.target.value)} placeholder="Python, research, project management" /></label>
          <label>Previous employers <span className="label-hint">comma separated</span><input value={form.previous_employers} onChange={(event) => setField('previous_employers', event.target.value)} placeholder="Internships, campus jobs, or companies" /></label>
          <label>Career interests <span className="label-hint">comma separated</span><input value={form.career_interests} onChange={(event) => setField('career_interests', event.target.value)} placeholder="Product, healthcare, fintech" /></label>
          <div className="form-grid">
            <label>Job types <span className="label-hint">comma separated</span><input value={form.preferred_job_types} onChange={(event) => setField('preferred_job_types', event.target.value)} placeholder="Internship, full-time" /></label>
            <label>Industries <span className="label-hint">comma separated</span><input value={form.preferred_industries} onChange={(event) => setField('preferred_industries', event.target.value)} placeholder="Technology, education" /></label>
          </div>
          <fieldset>
            <legend>Resume reference <span className="label-hint">optional</span></legend>
            <div className="form-grid">
              <label>File name<input value={form.resume_file_name} onChange={(event) => setField('resume_file_name', event.target.value)} placeholder="alex-chen-resume.pdf" /></label>
              <label>Secure file URL<input type="url" value={form.resume_url} onChange={(event) => setField('resume_url', event.target.value)} placeholder="https://…" /></label>
            </div>
            <p className="form-hint">You can skip this for now. Binary resume storage and parsing will be added with a later upload workflow.</p>
          </fieldset>
          {error && <p className="error-message" role="alert">{error}</p>}
          <button className="primary-button" disabled={isSubmitting}>{isSubmitting ? 'Saving profile…' : 'Continue to CareerConnect'}</button>
        </form>
      </section>
    </main>
  )
}
