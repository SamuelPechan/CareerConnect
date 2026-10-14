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

## Phase 1 setup

Phase 1 establishes the project foundation. Domain features such as authentication, applications, contacts, and reminders are intentionally added in later phases.

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

## Architecture direction

- React and TypeScript handle presentation and client-side API integration.
- FastAPI owns validation, authentication, authorization, business rules, and the REST contract.
- SQLAlchemy and Alembic provide the PostgreSQL persistence layer and migrations.
- External contact sources will be implemented behind provider interfaces. The first version will not scrape LinkedIn, Handshake, or other platforms.
- Message drafts always require user review and approval; CareerConnect never sends messages automatically.

## Planned phases

1. Foundation and local development setup
2. Authentication, profiles, and onboarding
3. Opportunities, applications, and dashboard basics
4. Companies and Find Contacts workflow
5. User-controlled contact discovery
6. Contacts, interactions, and reminders
7. Reviewed message drafts
8. Dashboard analytics
9. Tests, documentation, and CI
10. Production deployment
11. Optional browser-extension evaluation

## Known limitations

The repository currently contains only the Phase 1 foundation. Production deployment, authentication, domain data, integrations, and analytics are not yet implemented. The optional browser extension will remain separate from the core application.
