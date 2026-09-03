# Wardrobe Manager

A multi-user web app for cataloguing clothing, building outfits, and tracking wear.

## Stack

- **Backend:** FastAPI (Python 3.13) + SQLAlchemy + Alembic + PostgreSQL
- **Frontend:** React + Vite + TypeScript
- **Auth:** JWT access + refresh tokens
- **Images:** Cloudinary
- **Deploy:** Railway (single service, multi-stage Dockerfile)

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

## Status

Phase 0 — scaffolding. No application code yet.

## Local development

```bash
cp .env.example .env   # then fill in Cloudinary keys + JWT_SECRET
docker-compose up
```

- API: http://localhost:8000
- Web: http://localhost:5173
- API docs: http://localhost:8000/docs

## Project layout

```
backend/    FastAPI app, models, routers, Alembic migrations
frontend/   React + Vite single-page app
```
