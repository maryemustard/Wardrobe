# Wardrobe Manager

A multi-user web app for cataloguing clothing, building outfits, and tracking wear.

## Stack

- **Backend:** FastAPI (Python 3.13) + SQLAlchemy + Alembic + PostgreSQL
- **Frontend:** React + Vite + TypeScript
- **Auth:** JWT access + refresh tokens (Phase 1)
- **Images:** Cloudinary (Phase 3)
- **Deploy:** Railway (single service, multi-stage Dockerfile)

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

## Status

**Phase 0 — scaffold.** Runnable skeleton: `/api/health` endpoint, a React page that
pings it, Docker/Compose/CI wiring. No feature code yet.

## Local development

### Option A — Docker (matches production)

```bash
cp .env.example .env      # fill in JWT_SECRET; Cloudinary can wait until Phase 3
docker compose up --build
```

- Web: http://localhost:5173
- API: http://localhost:8000  ·  docs: http://localhost:8000/docs
- Postgres: localhost:5432 (`wardrobe` / `wardrobe`)

### Option B — run each part directly

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+psycopg://wardrobe:wardrobe@localhost:5432/wardrobe
uvicorn app.main:app --reload
```

```bash
# frontend
cd frontend
npm install
npm run dev
```

## Checks

```bash
cd backend  && ruff check . && pytest
cd frontend && npm run typecheck && npm run build
```

## Migrations

```bash
cd backend
alembic revision --autogenerate -m "message"   # after adding/changing models
alembic upgrade head
```

## Project layout

```
backend/
  app/            FastAPI app, config, db session
  alembic/        migration environment + versions
  tests/
frontend/
  src/            React + Vite single-page app
Dockerfile        multi-stage: build frontend, serve it from FastAPI
docker-compose.yml   local dev stack (db + api + web)
railway.toml      Railway build/start/healthcheck config
```

## Deploy (Railway)

1. New Railway project → **Deploy from GitHub repo** → pick `maryemustard/Wardrobe`.
2. Add the **PostgreSQL** plugin to the project.
3. In the app service **Variables**, set:
   - `DATABASE_URL` → reference the Postgres plugin's connection string
   - `JWT_SECRET` → a long random string
   - `CORS_ORIGINS` → the app's public URL
   - `ENVIRONMENT` → `prod`
4. Railway builds the Dockerfile, runs `alembic upgrade head`, and serves on `$PORT`.
   Health check: `/api/health`.
