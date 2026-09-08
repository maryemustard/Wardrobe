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
| Images    | Railway Volume                                      | Multipart upload to the API, saved on a mounted disk (`MEDIA_DIR`), served at `/media/*`; DB stores the relative URL + filename |
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
Items     GET  /items           filters: category, season, brand, q, archived; paginated
          POST /items           GET /items/{id}   PATCH /items/{id}   DELETE /items/{id}
          POST /items/{id}/image   (multipart)    DELETE /items/{id}/image

Outfits   GET  /outfits         POST /outfits (body has item_ids)
          GET  /outfits/{id}    PATCH /outfits/{id}   DELETE /outfits/{id}

Stats     GET  /stats           phase 2: counts by category, most/least worn, cost-per-wear

Health    GET  /api/health      unauthenticated, for Railway's health check
```

## 4. Image upload flow (Railway Volume)

1. User picks a photo in the item form (`<input type="file">`).
2. On save, the frontend creates/updates the item, then `POST`s the file as
   multipart to `/api/items/{id}/image`.
3. The backend validates type (JPEG/PNG/WebP/GIF) and size (<= 8 MB), writes it to
   `MEDIA_DIR/{id}.{ext}` on the mounted volume, and stores
   `image_url = /media/{id}.{ext}` + `image_public_id = {id}.{ext}` on the item.
4. FastAPI serves the file from `MEDIA_DIR` at `/media/*` (static mount).
5. Removing a photo, or deleting the item, unlinks the file.

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
      main.py          app, CORS, static SPA mount, /media mount
      config.py        pydantic-settings from env
      database.py      deps.py      security.py (Basic Auth)      media.py
      models/  schemas/  routers/
    alembic/  tests/  media/  (local uploads; gitignored)
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
| `MEDIA_DIR` | Where uploaded photos are stored; on Railway a path in the mounted volume (e.g. `/data/media`) |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `ENVIRONMENT` | `dev` / `prod` |

### Frontend (build-time, `VITE_` prefix)

| Var | Purpose |
|-----|---------|
| `VITE_API_BASE_URL` | API origin (empty string when same-origin single service) |

## 7. Deployment (Railway)

- One project: **PostgreSQL plugin** + **app service** (this repo) + a **Volume**
  mounted on the app service (e.g. at `/data`, with `MEDIA_DIR=/data/media`).
- Build: multi-stage Dockerfile.
  1. `node` stage: `npm ci && npm run build` in `frontend/` -> `frontend/dist`.
  2. `python` stage: install backend deps, copy `frontend/dist` into the image.
- The image `CMD` runs `alembic upgrade head`, then `uvicorn` on `$PORT`.
- FastAPI serves the SPA (SPA fallback for non-`/api` routes) and uploaded photos
  at `/media/*`.

## 8. Local development

- `docker compose up` starts Postgres, the API (reload), and the Vite dev server.
- The Vite dev server proxies `/api` and `/media` to the backend.
- Copy `.env.example` to `.env` and set the Basic Auth values. Uploads go to
  `backend/media/` locally.

## 9. Build phases

| Phase | Deliverable |
|-------|-------------|
| **0 – Scaffold** | Repo, both skeletons, docker-compose, CI, empty shell on Railway — **done** |
| **1 – Access + Items** | Basic Auth dependency; Item model + migration; filtered CRUD endpoints; wardrobe grid, item form, detail view, archive/delete — **done** |
| **2 – Images** | Railway Volume storage; `POST/DELETE /items/{id}/image`; file input in the item form; photos shown on cards + detail — **done** |
| **3 – Outfits** | Outfit + `outfit_items` join, `/api/outfits` CRUD with an item-id set, Outfits list / builder (item checklist) / detail pages, nav — **done** |
| **4 – Polish** | WearLog, stats dashboard, tags, search, responsive styling, empty states |
