# Database

CareerConnect uses PostgreSQL in development and production. The local database is provisioned by the root `docker-compose.yml` file.

Alembic migrations live under `backend/migrations`. Domain tables will be added incrementally with the relevant feature phases so each migration remains reviewable.

The application reads the database URL from `DATABASE_URL`; credentials must never be committed to source control.
