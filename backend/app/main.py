from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings

settings = get_settings()

app = FastAPI(title="Wardrobe Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


# In the production image the built SPA is copied in and served from here.
# In local dev SPA_DIST_DIR is unset and Vite serves the frontend separately.
_dist = Path(settings.spa_dist_dir) if settings.spa_dist_dir else None
if _dist and _dist.is_dir():
    app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str) -> FileResponse:
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = _dist / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_dist / "index.html")
