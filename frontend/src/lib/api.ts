export type User = {
  id: string
  email: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type Profile = {
  id: string
  user_id: string
  school: string | null
  major: string | null
  graduation_year: number | null
  skills: string[]
  previous_employers: string[]
  locations: string[]
  career_interests: string[]
  preferred_job_types: string[]
  preferred_industries: string[]
  onboarding_completed: boolean
  created_at: string
  updated_at: string
}

export type AuthResponse = {
  access_token: string
  token_type: string
  user: User
}

export type ProfileUpdate = Partial<Omit<Profile, 'id' | 'user_id' | 'created_at' | 'updated_at'>>

export type ResumeCreate = {
  file_name: string
  file_url?: string
  metadata?: Record<string, string>
}

export type Opportunity = {
  id: string
  user_id: string
  company_id: string | null
  title: string
  company_name: string
  location: string | null
  job_url: string | null
  source_platform: string | null
  description: string | null
  date_saved: string
  notes: string | null
  status: string
  created_at: string
  updated_at: string
  application: ApplicationSummary | null
}

export type ApplicationSummary = {
  id: string
  status: string
  application_date: string | null
  resume_id: string | null
  notes: string | null
}

export type Application = ApplicationSummary & {
  user_id: string
  opportunity_id: string
  created_at: string
  updated_at: string
  opportunity: Opportunity
}

export type OpportunityCreate = {
  title: string
  company_name: string
  location?: string
  job_url?: string
  source_platform?: string
  description?: string
  notes?: string
  status?: 'saved' | 'planning_to_apply'
}

export type DiscoveryLink = {
  id: string
  search_id: string
  platform: string
  search_url: string
  query: string
  relationship_reason: string
  reviewed: boolean
  created_at: string
  updated_at: string
}

export type DiscoverySearch = {
  id: string
  user_id: string
  opportunity_id: string
  company_id: string | null
  criteria: Record<string, unknown>
  relationship_categories: string[]
  instructions: string
  links: DiscoveryLink[]
  created_at: string
  updated_at: string
}

export type Contact = {
  id: string
  user_id: string
  company_id: string | null
  opportunity_id: string | null
  name: string
  job_title: string | null
  company_name: string
  school: string | null
  relationship_reason: string
  source_platform: string
  profile_url: string | null
  email: string | null
  notes: string | null
  relationship_status: string
  created_at: string
  updated_at: string
}

export type ContactCreate = {
  name: string
  job_title?: string
  company_name: string
  school?: string
  relationship_reason: string
  source_platform: string
  profile_url?: string
  email?: string
  notes?: string
  relationship_status?: string
  company_id?: string
  opportunity_id?: string
}

export type DashboardSummary = {
  total_saved_opportunities: number
  total_applications: number
  applications_by_status: Record<string, number>
  total_interviews: number
  total_offers: number
  total_contacts: number
  upcoming_follow_ups: number
  overdue_follow_ups: number
  total_interactions: number
  total_discovery_links: number
  reviewed_discovery_links: number
  applications_with_contacts: number
  applications_without_contacts: number
  interview_rate: number | null
  offer_rate: number | null
}

export type Interaction = {
  id: string
  user_id: string
  contact_id: string
  interaction_type: string
  occurred_at: string
  notes: string | null
  outcome: string | null
  next_steps: string | null
  created_at: string
  updated_at: string
}

export type Reminder = {
  id: string
  user_id: string
  contact_id: string | null
  opportunity_id: string | null
  interaction_id: string | null
  title: string
  due_at: string
  notes: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

export type MessageDraft = {
  id: string
  user_id: string
  contact_id: string
  opportunity_id: string | null
  message_type: string
  subject: string | null
  body: string
  status: string
  generated_context: Record<string, unknown>
  created_at: string
  updated_at: string
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers)
  headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null
    throw new Error(body?.detail ?? 'Something went wrong. Please try again.')
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  register: (email: string, password: string) =>
    request<AuthResponse>('/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) }),
  login: (email: string, password: string) =>
    request<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  currentUser: (token: string) => request<User>('/auth/me', {}, token),
  logout: (token: string) => request<void>('/auth/logout', { method: 'POST' }, token),
  getProfile: (token: string) => request<Profile>('/profile', {}, token),
  updateProfile: (token: string, profile: ProfileUpdate) =>
    request<Profile>('/profile', { method: 'PATCH', body: JSON.stringify(profile) }, token),
  createResume: (token: string, resume: ResumeCreate) =>
    request('/profile/resumes', { method: 'POST', body: JSON.stringify(resume) }, token),
  getDashboardSummary: (token: string) => request<DashboardSummary>('/dashboard/summary', {}, token),
  listOpportunities: (token: string, params: URLSearchParams = new URLSearchParams()) =>
    request<Opportunity[]>(`/opportunities?${params.toString()}`, {}, token),
  createOpportunity: (token: string, opportunity: OpportunityCreate) =>
    request<Opportunity>('/opportunities', { method: 'POST', body: JSON.stringify(opportunity) }, token),
  updateOpportunity: (token: string, id: string, opportunity: Partial<OpportunityCreate>) =>
    request<Opportunity>(`/opportunities/${id}`, { method: 'PATCH', body: JSON.stringify(opportunity) }, token),
  deleteOpportunity: (token: string, id: string) =>
    request<void>(`/opportunities/${id}`, { method: 'DELETE' }, token),
  applyToOpportunity: (token: string, id: string) =>
    request<Application>(`/opportunities/${id}/apply`, { method: 'POST' }, token),
  listApplications: (token: string, params: URLSearchParams = new URLSearchParams()) =>
    request<Application[]>(`/applications?${params.toString()}`, {}, token),
  updateApplication: (token: string, id: string, application: { status?: string; notes?: string }) =>
    request<Application>(`/applications/${id}`, { method: 'PATCH', body: JSON.stringify(application) }, token),
  findContacts: (token: string, opportunityId: string) =>
    request<DiscoverySearch>(`/discovery/opportunities/${opportunityId}/find-contacts`, { method: 'POST' }, token),
  reviewDiscoveryLink: (token: string, linkId: string, reviewed: boolean) =>
    request<DiscoveryLink>(`/discovery/links/${linkId}`, { method: 'PATCH', body: JSON.stringify({ reviewed }) }, token),
  createContact: (token: string, contact: ContactCreate) =>
    request<Contact>('/contacts', { method: 'POST', body: JSON.stringify(contact) }, token),
  listContacts: (token: string, params: URLSearchParams = new URLSearchParams()) =>
    request<Contact[]>(`/contacts?${params.toString()}`, {}, token),
  getContact: (token: string, id: string) => request<Contact>(`/contacts/${id}`, {}, token),
  connectContact: (token: string, contactId: string, applicationId: string) =>
    request(`/contacts/${contactId}/applications/${applicationId}`, { method: 'POST' }, token),
  listInteractions: (token: string, contactId: string) =>
    request<Interaction[]>(`/contacts/${contactId}/interactions`, {}, token),
  createInteraction: (token: string, contactId: string, interaction: { interaction_type: string; notes?: string; outcome?: string; next_steps?: string }) =>
    request<Interaction>(`/contacts/${contactId}/interactions`, { method: 'POST', body: JSON.stringify(interaction) }, token),
  listReminders: (token: string, params: URLSearchParams = new URLSearchParams()) =>
    request<Reminder[]>(`/reminders?${params.toString()}`, {}, token),
  createReminder: (token: string, reminder: { title: string; due_at: string; notes?: string; contact_id?: string; opportunity_id?: string; interaction_id?: string }) =>
    request<Reminder>('/reminders', { method: 'POST', body: JSON.stringify(reminder) }, token),
  updateReminder: (token: string, id: string, reminder: { completed?: boolean; title?: string; due_at?: string; notes?: string }) =>
    request<Reminder>(`/reminders/${id}`, { method: 'PATCH', body: JSON.stringify(reminder) }, token),
  generateMessageDraft: (token: string, draft: { contact_id: string; opportunity_id?: string; message_type: string }) =>
    request<MessageDraft>('/message-drafts/generate', { method: 'POST', body: JSON.stringify(draft) }, token),
  listMessageDrafts: (token: string, params: URLSearchParams = new URLSearchParams()) =>
    request<MessageDraft[]>(`/message-drafts?${params.toString()}`, {}, token),
  updateMessageDraft: (token: string, id: string, draft: { subject?: string; body?: string; status?: string }) =>
    request<MessageDraft>(`/message-drafts/${id}`, { method: 'PATCH', body: JSON.stringify(draft) }, token),
}
