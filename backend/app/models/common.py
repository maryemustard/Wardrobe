import uuid
from datetime import UTC, datetime


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    """Naive UTC timestamp for DateTime columns."""
    return datetime.now(UTC).replace(tzinfo=None)
