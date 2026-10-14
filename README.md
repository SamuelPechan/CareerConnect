# CareerConnect

CareerConnect is a networking-first job-search CRM for college students and early-career professionals. It connects job opportunities to professional contacts, conversations, reminders, and user-reviewed message drafts.

CareerConnect is not a job board, automatic application bot, or mass-outreach tool. Contact discovery is user-controlled: the application generates search criteria and external links, and the user reviews and confirms contacts before saving them.

## Repository structure

```text
frontend/     React + TypeScript + Vite web application
backend/      FastAPI REST API and SQLAlchemy database layer
database/     Database and migration notes
.github/      CI workflows
```

## Current implementation

Phases 1–3 established the project foundation, JWT authentication, profiles, onboarding, job opportunities, applications, safe filtering/sorting, status tracking, and dashboard basics. Phase 4 adds user-owned companies and a user-controlled Find Contacts workflow that generates search criteria and external links without scraping or automatic outreach.

### Prerequisites

- Node.js 20+
- npm 10+
- Python 3.12+
- Docker Desktop

### Local setup

1. Copy `.env.example` to `.env` and update secrets for any non-local environment.
2. Start PostgreSQL:

   ```powershell
   docker compose up -d postgres
   ```

3. Create and activate a Python virtual environment:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r backend\requirements.txt
   ```

4. Start the API:

   ```powershell
   uvicorn app.main:app --app-dir backend --reload
   ```

5. Install and start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

The frontend runs at `http://localhost:5173`. The API runs at `http://localhost:8000` and exposes OpenAPI documentation at `/docs`.

### Checks

```powershell
cd frontend
npm run lint
npm run build
```

```powershell
cd backend
ruff check .
pytest
```

The backend commands require Python 3.12+ and installed dependencies.

### Authentication and onboarding API

- `POST /api/v1/auth/register` — create an account and receive a bearer token
- `POST /api/v1/auth/login` — authenticate with email and password
- `GET /api/v1/auth/me` — return the current authenticated user
- `POST /api/v1/auth/logout` — client logout endpoint; the short-lived token is removed client-side
- `GET /api/v1/profile` — return the authenticated user’s profile
- `PATCH /api/v1/profile` — update onboarding/profile information
- `GET /api/v1/profile/resumes` — list the user’s resume references
- `POST /api/v1/profile/resumes` — save a user-provided resume reference

### Opportunities, applications, and dashboard API

- `GET /api/v1/opportunities` — list opportunities with safe status/source/company filters and sorting
- `POST /api/v1/opportunities` — save a job opportunity
- `GET /api/v1/opportunities/{id}` — view one opportunity
- `PATCH /api/v1/opportunities/{id}` — update an opportunity
- `DELETE /api/v1/opportunities/{id}` — delete an opportunity
- `POST /api/v1/opportunities/{id}/apply` — convert an opportunity into an application
- `GET /api/v1/applications` — list applications with safe status/source/company filters and sorting
- `GET /api/v1/applications/{id}` — view one application
- `PATCH /api/v1/applications/{id}` — update application status, notes, date, or resume reference
- `DELETE /api/v1/applications/{id}` — remove an application while keeping the opportunity
- `GET /api/v1/dashboard/summary` — return opportunity and application pipeline counts
- `GET /api/v1/companies` — list the user’s saved companies
- `POST /api/v1/companies` — create or reuse a user-owned company record
- `GET /api/v1/companies/{id}` — view one company
- `GET /api/v1/companies/{id}/opportunities` — list opportunities for a company
- `POST /api/v1/discovery/opportunities/{id}/find-contacts` — generate a user-reviewed contact search plan
- `GET /api/v1/discovery/searches/{id}` — retrieve a saved search plan
- `PATCH /api/v1/discovery/links/{id}` — mark an external search link reviewed or unreviewed

All profile and resume endpoints require `Authorization: Bearer <token>`. User records are isolated by the authenticated user ID. Phase 2 stores resume metadata and an optional permitted URL; binary storage and parsing will be added later with explicit user review.

## Architecture direction

- React and TypeScript handle presentation and client-side API integration.
- FastAPI owns validation, authentication, authorization, business rules, and the REST contract.
- SQLAlchemy and Alembic provide the PostgreSQL persistence layer and migrations.
- External contact sources will be implemented behind provider interfaces. The first version will not scrape LinkedIn, Handshake, or other platforms.
- Message drafts always require user review and approval; CareerConnect never sends messages automatically.

## Planned phases

1. Foundation and local development setup — complete
2. Authentication, profiles, and onboarding — complete
3. Opportunities, applications, and dashboard basics — complete
4. Companies and Find Contacts workflow — complete
5. User-controlled contact discovery
6. Contacts, interactions, and reminders
7. Reviewed message drafts
8. Dashboard analytics
9. Tests, documentation, and CI
10. Production deployment
11. Optional browser-extension evaluation

## Known limitations

Production deployment, external provider integrations, contact persistence, messaging, and analytics are not yet implemented. The optional browser extension will remain separate from the core application.
