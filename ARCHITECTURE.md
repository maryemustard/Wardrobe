# Wardrobe Manager — Architecture

A **single-user** web app for cataloguing clothing, building outfits, and tracking
wear. One person (the owner) uses it. Deployed on Railway.

## 1. Stack

| Layer     | Choice                                              | Notes |
|-----------|----------------------------------------------------|-------|
| Backend   | FastAPI (Python 3.13), Uvicorn                      | SQLAlchemy 2.0 + Alembic migrations, Pydantic v2 |
| Database  | PostgreSQL                                          | Railway managed plugin; `DATABASE_URL` injected |
| Frontend  | React + Vite + TypeScript                           | React Router, TanStack Query for server state |
| Access    | HTTP Basic Auth, single credential                  | `BASIC_AUTH_USER` / `BASIC_AUTH_PASS` env vars, checked by FastAPI middleware. No user accounts, no signup, no JWT. |
| Images    | Cloudinary (free tier)                              | Browser uploads directly via signed params; DB stores `secure_url` + `public_id` |
| Deploy    | Railway, single service via multi-stage Dockerfile  | Node build stage -> Python runtime; FastAPI serves `/api/*` and the built SPA at `/` |
| CI        | GitHub Actions                                      | Lint + test on PR |

If stronger isolation is wanted later, put Tailscale or Cloudflare Access in
front of the Railway service — no app changes needed.

## 2. Data model

No `User` table. Everything belongs to the single owner implicitly.

### v1

- **Item** (a garment) — `id`, `name`, `category` (enum: top/bottom/dress/outerwear/shoes/accessory),
  `color`, `brand`, `size`, `season` (spring/summer/fall/winter/all), `material`,
  `purchase_date`, `price`, `notes`, `image_url`, `image_public_id`,
  `is_archived`, `created_at`, `updated_at`
- **Outfit** — `id`, `name`, `occasion`, `notes`, `created_at`
- **OutfitItem** — join table (`outfit_id`, `item_id`), many-to-many

### Phase 2

- **WearLog** — `id`, `item_id?`, `outfit_id?`, `worn_on (date)`, `notes`
  — enables cost-per-wear and "least worn".
- **Tag** + **ItemTag** — free-form tags.

## 3. API surface (`/api` prefix)

Every endpoint requires HTTP Basic Auth.

```
Items     GET  /items           filters: category, color, season, brand, q, archived; paginated
          POST /items           GET /items/{id}   PATCH /items/{id}   DELETE /items/{id}

Uploads   POST /uploads/sign    -> Cloudinary signature params for direct browser upload

Outfits   GET  /outfits         POST /outfits (body has item_ids)
          GET  /outfits/{id}    PATCH /outfits/{id}   DELETE /outfits/{id}

Stats     GET  /stats           phase 2: counts by category, most/least worn, cost-per-wear

Health    GET  /api/health      unauthenticated, for Railway's health check
```

## 4. Image upload flow (Cloudinary, signed)

1. User picks a photo in the item form.
2. Frontend calls `POST /api/uploads/sign` -> backend returns
   `{ timestamp, signature, api_key, cloud_name, folder }` signed with the API secret.
3. Frontend uploads the file directly to Cloudinary, receives `secure_url` + `public_id`.
4. Frontend saves the item with those two fields.
5. On item delete, backend calls Cloudinary `destroy(public_id)`.

## 5. Repo structure

```
wardrobe/
  README.md   ARCHITECTURE.md   .gitignore   .env.example
  Dockerfile                      multi-stage build
  railway.toml                    build / start / release (alembic upgrade head)
  docker-compose.yml              local: postgres + api + web
  backend/
    pyproject.toml
    app/
      main.py          app, CORS, Basic Auth dependency, static SPA mount
      config.py        pydantic-settings from env
      database.py      deps.py
      models/  schemas/  routers/  services/    cloudinary.py
    alembic/  tests/
  frontend/
    package.json  vite.config.ts  index.html
    src/  api/  pages/  components/  lib/
  .github/workflows/ci.yml
```

## 6. Environment variables

### Backend

| Var | Purpose |
|-----|---------|
| `DATABASE_URL` | Postgres connection (Railway provides) |
| `BASIC_AUTH_USER` | Username for the app's Basic Auth gate |
| `BASIC_AUTH_PASS` | Password for the app's Basic Auth gate |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | Image hosting |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `ENVIRONMENT` | `dev` / `prod` |

### Frontend (build-time, `VITE_` prefix)

| Var | Purpose |
|-----|---------|
| `VITE_API_BASE_URL` | API origin (empty string when same-origin single service) |
| `VITE_CLOUDINARY_CLOUD_NAME` | Used to build image URLs |

## 7. Deployment (Railway)

- One project: **PostgreSQL plugin** + **app service** (this repo).
- Build: multi-stage Dockerfile.
  1. `node` stage: `npm ci && npm run build` in `frontend/` -> `frontend/dist`.
  2. `python` stage: install backend deps, copy `frontend/dist` into the image.
- Release command: `alembic upgrade head`.
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- FastAPI mounts `frontend/dist` as static files with an SPA fallback to `index.html`
  for non-`/api` routes.

## 8. Local development

- `docker compose up` starts Postgres, the API (reload), and the Vite dev server.
- The Vite dev server proxies `/api` to the backend.
- Copy `.env.example` to `.env` and fill in Cloudinary keys + Basic Auth values.

## 9. Build phases

| Phase | Deliverable |
|-------|-------------|
| **0 – Scaffold** | Repo, both skeletons, docker-compose, CI, empty shell on Railway — **done** |
| **1 – Access + Items** | Basic Auth dependency; Item model + migration; filtered CRUD endpoints; wardrobe grid, item form, detail view, archive/delete — **done** |
| **2 – Images** | `/uploads/sign`, upload component wired into item form, cleanup on delete |
| **3 – Outfits** | Outfit + join models, endpoints, outfit pages with item picker |
| **4 – Polish** | WearLog, stats dashboard, tags, search, responsive styling, empty states |
