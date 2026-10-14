import { useAuth } from '../auth/AuthContext'

export default function DashboardPage() {
  const { user, profile, logout } = useAuth()
  return (
    <main className="dashboard-shell">
      <nav className="topbar"><span className="brand">CareerConnect</span><button className="text-button" onClick={() => void logout()}>Log out</button></nav>
      <section className="dashboard-content">
        <p className="eyebrow">Your workspace</p>
        <h1>Build momentum through people.</h1>
        <p className="muted">You’re signed in as {user?.email}. Your profile is ready for the next step: connecting applications to relevant contacts.</p>
        <div className="dashboard-grid">
          <article className="metric-card"><span>Profile</span><strong>Complete</strong><small>{profile?.school || 'School not added'}</small></article>
          <article className="metric-card"><span>Skills</span><strong>{profile?.skills.length ?? 0}</strong><small>Ready to match with opportunities</small></article>
          <article className="metric-card"><span>Next up</span><strong>Add an opportunity</strong><small>Applications and contact discovery arrive in Phase 3.</small></article>
        </div>
      </section>
    </main>
  )
}
