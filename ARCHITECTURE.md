# Wardrobe Manager — Architecture

A multi-user web app for cataloguing clothing, building outfits, and tracking wear.
Deployed on Railway.

## 1. Stack

| Layer     | Choice                                              | Notes |
|-----------|----------------------------------------------------|-------|
| Backend   | FastAPI (Python 3.13), Uvicorn                      | SQLAlchemy 2.0 + Alembic migrations, Pydantic v2 |
| Database  | PostgreSQL                                          | Railway managed plugin; `DATABASE_URL` injected |
| Frontend  | React + Vite + TypeScript                           | React Router, TanStack Query for server state |
| Auth      | JWT access + refresh tokens, hand-rolled            | `passlib[bcrypt]` hashing, `PyJWT` tokens, OAuth2 password flow |
| Images    | Cloudinary (free tier)                              | Browser uploads directly via signed params; DB stores `secure_url` + `public_id` |
| Deploy    | Railway, single service via multi-stage Dockerfile  | Node build stage → Python runtime; FastAPI serves `/api/*` and the built SPA at `/` |
| CI        | GitHub Actions                                      | Lint + test on PR |

Splitting the frontend into its own Railway static service later is a small change
(add `VITE_API_BASE_URL`, configure CORS).

## 2. Data model

### v1

- **User** — `id (uuid)`, `email (unique)`, `hashed_password`, `display_name`, `created_at`
- **Item** (a garment) — `id`, `user_id`, `name`, `category` (enum: top/bottom/dress/outerwear/shoes/accessory),
  `color`, `brand`, `size`, `season` (spring/summer/fall/winter/all), `material`,
  `purchase_date`, `price`, `notes`, `image_url`, `image_public_id`,
  `is_archived`, `created_at`, `updated_at`
- **Outfit** — `id`, `user_id`, `name`, `occasion`, `notes`, `created_at`
- **OutfitItem** — join table (`outfit_id`, `item_id`), many-to-many

### Phase 2

- **WearLog** — `id`, `user_id`, `item_id?`, `outfit_id?`, `worn_on (date)`, `notes`
  — enables cost-per-wear and "least worn".
- **Tag** + **ItemTag** — free-form user tags.

Every Item/Outfit query is scoped to `current_user.id`.

## 3. API surface (`/api` prefix)

```
Auth      POST /auth/register   POST /auth/login   POST /auth/refresh
          POST /auth/logout     GET  /auth/me

Items     GET  /items           filters: category, color, season, brand, q, archived; paginated
          POST /items           GET /items/{id}   PATCH /items/{id}   DELETE /items/{id}

Uploads   POST /uploads/sign    -> Cloudinary signature params for direct browser upload

Outfits   GET  /outfits         POST /outfits (body has item_ids)
          GET  /outfits/{id}    PATCH /outfits/{id}   DELETE /outfits/{id}

Stats     GET  /stats           phase 2: counts by category, most/least worn, cost-per-wear
```

## 4. Image upload flow (Cloudinary, signed)

1. User picks a photo in the item form.
2. Frontend calls `POST /api/uploads/sign` (authenticated) -> backend returns
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
      main.py          app, CORS, static SPA mount
      config.py        pydantic-settings from env
      database.py      deps.py
      models/  schemas/  routers/  services/    cloudinary.py, security.py
    alembic/  tests/
  frontend/
    package.json  vite.config.ts  index.html
    src/  api/  auth/  pages/  components/  lib/
  .github/workflows/ci.yml
```

## 6. Environment variables

### Backend

| Var | Purpose |
|-----|---------|
| `DATABASE_URL` | Postgres connection (Railway provides) |
| `JWT_SECRET` | Token signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Default 14 |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | Image hosting |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `ENVIRONMENT` | `dev` / `prod` |

### Frontend (build-time, `VITE_` prefix)

| Var | Purpose |
|-----|---------|
| `VITE_API_BASE_URL` | API origin (empty string when same-origin single service) |
| `VITE_CLOUDINARY_CLOUD_NAME` | Used to build image URLs |

## 7. Deployment (Railway)

- One project, two pieces: **PostgreSQL plugin** + **app service** (this repo).
- Build: multi-stage Dockerfile.
  1. `node` stage: `npm ci && npm run build` in `frontend/` -> `frontend/dist`.
  2. `python` stage: install backend deps, copy `frontend/dist` into the image.
- Release command: `alembic upgrade head`.
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- FastAPI mounts `frontend/dist` as static files with an SPA fallback to `index.html`
  for non-`/api` routes.

## 8. Local development

- `docker-compose up` starts Postgres, the API (reload), and the Vite dev server.
- Frontend dev server proxies `/api` to the backend.
- Copy `.env.example` to `.env` and fill in Cloudinary + a local `JWT_SECRET`.

## 9. Build phases

| Phase | Deliverable |
|-------|-------------|
| **0 – Scaffold** | Repo, both skeletons, docker-compose, CI, deploy the empty shell to Railway early |
| **1 – Auth** | User model, register/login/me/refresh, frontend auth pages + route guard |
| **2 – Items CRUD** | Item model + migration, filtered/paginated endpoints, wardrobe grid, item form (no photo), detail view |
| **3 – Images** | `/uploads/sign`, upload component wired into item form, cleanup on delete |
| **4 – Outfits** | Outfit + join models, endpoints, outfit pages with item picker |
| **5 – Polish** | WearLog, stats dashboard, tags, search, responsive styling, empty states |
