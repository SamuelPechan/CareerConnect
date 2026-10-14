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
}
