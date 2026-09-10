"""AI outfit suggestions, powered by Claude. Optional — needs an API key
(set on the /settings/ page, or via the ANTHROPIC_API_KEY env var)."""

import json

import anthropic
from django.conf import settings

_MODEL = "claude-opus-5"
_MAX_ITEMS = 300

_SYSTEM = """You are a friendly personal stylist. You get the user's wardrobe as a list \
of items (each with an id and attributes) and a short "vibe" for today. Pick a cute, \
sensible outfit using ONLY the given item ids.

- Usually one top + one bottom, OR one dress; add outerwear, shoes, and at most one \
accessory when they fit the vibe or weather.
- Match the vibe and any weather hints.
- Only ever use ids that appear in the wardrobe. Never invent items.
- If the wardrobe can't really cover the vibe, pick the closest fit and say so.

Return the chosen item ids and one or two upbeat sentences about the look."""

_SCHEMA = {
    "type": "object",
    "properties": {
        "item_ids": {"type": "array", "items": {"type": "integer"}},
        "rationale": {"type": "string"},
    },
    "required": ["item_ids", "rationale"],
    "additionalProperties": False,
}


class StylistUnavailable(RuntimeError):
    """The stylist could not produce a suggestion (no key, upstream error, ...)."""


def _api_key() -> str:
    from .models import AppSettings

    return settings.ANTHROPIC_API_KEY or AppSettings.load().anthropic_api_key


def suggest_outfit(vibe, items):
    """Return (chosen item ids, rationale). Raises StylistUnavailable on any failure."""
    key = _api_key()
    if not key:
        raise StylistUnavailable("AI suggestions are not set up yet — add your API key in Settings.")
    if not items:
        raise StylistUnavailable("Add a few items to your wardrobe first!")

    brief = [
        {
            "id": i.id,
            "name": i.name,
            "category": i.category,
            "description": i.description or None,
        }
        for i in items[:_MAX_ITEMS]
    ]
    user = f"Wardrobe:\n{json.dumps(brief, indent=2)}\n\nToday's vibe: {vibe.strip()}"

    try:
        response = anthropic.Anthropic(api_key=key, timeout=60).messages.create(
            model=_MODEL,
            max_tokens=8000,
            system=_SYSTEM,
            output_config={
                "effort": "low",
                "format": {"type": "json_schema", "schema": _SCHEMA},
            },
            messages=[{"role": "user", "content": user}],
        )
    except anthropic.APIError as exc:
        raise StylistUnavailable(f"The stylist is unavailable right now ({exc}).") from exc

    text = next((b.text for b in response.content if b.type == "text"), "")
    try:
        data = json.loads(text)
        return [int(x) for x in data["item_ids"]], str(data["rationale"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise StylistUnavailable("The stylist gave an unexpected answer — try again.") from exc
