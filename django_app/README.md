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
  item (or swap/clear its photo) and save.
- Saved items persist across refreshes (SQLite; photos in `media/`).
- Missing name → inline error. Non-image or >8 MB photo → inline error. No crash.
- Empty wardrobe shows a "add your first one" message.

No HTMX, no JavaScript build step — plain form POSTs with redirects.

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

Covers: the page loads with the empty state; a valid item saves, redirects,
and shows in the grid; a blank name is rejected with a message and no row
saved; a non-image upload is rejected; the edit page is prefilled; editing
updates the item; editing a missing id is a 404. (7 tests.)

## Config (deploy only)

Local dev reads no environment variables. For deployment, copy `.env.example`
to `.env` and set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, and
`DJANGO_ALLOWED_HOSTS`. `settings.py` reads these from the environment.

## Layout

```
django_app/
  pyproject.toml            uv project (Django, Pillow)
  manage.py
  config/                   project settings, urls, wsgi/asgi
  wardrobe/                 the one app
    models.py               Item(name, category, description, photo, created_at)
    forms.py                ItemForm + photo size check
    views.py                wardrobe (list + create) and edit_item
    templates/wardrobe/     wardrobe.html, edit.html, _form_fields.html
    tests.py
  media/                    uploaded photos (gitignored)
  db.sqlite3               local database (gitignored)
```
