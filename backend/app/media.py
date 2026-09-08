from pathlib import Path

from app.config import get_settings
from app.models.item import Item

# content-type -> file extension for images we accept
ALLOWED_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_BYTES = 8 * 1024 * 1024


def media_dir() -> Path:
    d = Path(get_settings().media_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def delete_image_file(item: Item) -> None:
    """Remove the file backing an item's photo, if any. Safe to call always."""
    if not item.image_public_id:
        return
    (media_dir() / item.image_public_id).unlink(missing_ok=True)
