# Wardrobe — Django MVP

The smallest runnable version of the wardrobe idea, built for the ENTR 5000
class stack: **Django + templates + Bootstrap + SQLite**, managed with **uv**.
One Django app (`wardrobe`), one page.

See [`../SPEC.md`](../SPEC.md) for what "done" means. This directory is separate
from the repo's other app (`backend/` + `frontend/`) and does not touch it.

## What it does

Main page at `/`:

- A form to add a clothing item — **name**, **category**, **description**, **photo**.
- A grid of everything you've saved, newest first, with the photo on each card
  (or a category placeholder if there's no photo).
- Each card has an **Edit** link → `/<id>/edit/`, a prefilled form to change the
  item (or swap/clear its photo) and save, plus a **Delete this item** button
  (with a confirm) that removes the item and its photo file.
- Wear tracking: each card shows **👕 worn N×** with a **+ wore it** button
  (logs today) and an **undo**; the edit page shows the total and last-worn date.
- `/suggest/` — type a "vibe" and Claude picks an outfit from your wardrobe with
  a short blurb. Optional AI feature.
- `/settings/` — paste your Anthropic API key here (saved in the local database;
  gitignored) so `/suggest/` works without touching environment variables. The
  `ANTHROPIC_API_KEY` env var still works and takes priority if set.
- Saved items persist across refreshes (SQLite; photos in `media/`).
- Missing name → inline error. Non-image or >8 MB photo → inline error. No crash.
- Empty wardrobe shows a "add your first one" message.

No HTMX, no JavaScript build step — plain form POSTs with redirects.

Styling is a small inline theme in `base.html` (Google Fonts + a `<style>`
block over Bootstrap): soft pink/cream palette, rounded cards, and category
emojis (👕 👖 👗 🧥 👟 👜) from `Item.emoji`.

## Run it locally

### With uv (the class way)

If you don't have uv yet, install it once:
<https://docs.astral.sh/uv/getting-started/installation/> — then reopen your
terminal.

```bash
cd django_app
uv sync                              # creates .venv, installs Django + Pillow
uv run python manage.py migrate      # creates the SQLite tables
uv run python manage.py runserver    # starts the dev server
```

### Without uv (plain virtualenv)

```bash
cd django_app
python3 -m venv .venv
source .venv/bin/activate
pip install "django>=5.2,<6" "pillow>=10"
python manage.py migrate
python manage.py runserver
```

Then open **<http://127.0.0.1:8000/>**. Stop the server with **Ctrl-C**.

## Verify it works

1. The page loads and shows the "Add an item" form with an empty-state message.
2. Fill in a name, pick a category, (optionally) choose a photo, click **Save item**.
3. The item appears in the grid on the right, with its photo.
4. **Refresh the page** — the item is still there.
5. Submit with the name blank → you get a red "This field is required" message and
   nothing is saved.

## Run the test

```bash
uv run python manage.py test          # or: python manage.py test
```

Covers: page loads with the empty state; a valid item saves, redirects, and
shows in the grid; a blank name is rejected with a message and no row saved;
a non-image upload is rejected; the edit page is prefilled; editing updates
the item; editing a missing id is a 404; the suggest page loads; suggesting
with no API key shows a message (no crash); a mocked suggestion renders the
picked items; the settings page loads and saves / keeps / clears the API key;
the stylist reads the saved key; delete removes an item (POST), a GET bounces
to edit, deleting a missing id is a 404; logging a wear increments the count,
undo decrements, undo with no wears is safe, the count shows on the grid.
(22 tests.)

## Deploy to Railway

The app is production-ready: Gunicorn, WhiteNoise for static files, PostgreSQL
via `DATABASE_URL` (SQLite locally), a `Procfile` that runs `migrate` +
`collectstatic` before starting. It builds with Nixpacks — no Dockerfile.

1. Railway → **New Project → Deploy from GitHub repo** → this repo.
2. On the service: **Settings → Root Directory** = `django_app`.
3. **+ Create → Database → PostgreSQL** in the project.
4. **+ Create → Volume**, mount path `/data` (keeps uploaded photos).
5. Service **Variables**:
   | Name | Value |
   |---|---|
   | `DATABASE_URL` | reference `Postgres.DATABASE_URL` |
   | `DJANGO_SECRET_KEY` | a long random string |
   | `DJANGO_DEBUG` | `false` |
   | `DJANGO_ALLOWED_HOSTS` | the generated domain, no `https://` |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://` + the generated domain |
   | `DJANGO_MEDIA_ROOT` | `/data/media` |
   | `ANTHROPIC_API_KEY` | optional (or set it in the app's Settings page) |
6. **Settings → Networking → Generate Domain**, then put that exact host in
   `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` and redeploy.

`settings.py` reads every one of these from the environment.

## Layout

```
django_app/
  pyproject.toml            uv project (Django, Pillow)
  manage.py
  config/                   project settings, urls, wsgi/asgi
  wardrobe/                 the one app
    models.py               Item (+ .emoji, .wear_count, .last_worn); Wear; AppSettings
    forms.py                ItemForm; ApiKeyForm
    views.py                wardrobe, edit_item, delete_item, log_wear, unlog_wear, suggest, settings_page
    stylist.py              Claude call for /suggest/ (key from Settings or env)
    templates/wardrobe/     wardrobe / edit / suggest / settings / _form_fields
    tests.py
  media/                    uploaded photos (gitignored)
  db.sqlite3               local database (gitignored)
```
