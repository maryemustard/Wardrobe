"""AI outfit suggestions, powered by Claude."""

import json

import anthropic

from app.config import get_settings
from app.models.item import Item

_MODEL = "claude-opus-5"
_MAX_ITEMS = 400

_SYSTEM = """You are a personal stylist. You get the user's wardrobe as a list of items \
(each with an id and attributes) and a short description of what they are doing today. \
Choose a single sensible outfit using ONLY the given items.

Guidelines:
- A typical outfit is one top + one bottom, OR one dress; then add outerwear, shoes, and at \
most one or two accessories when they suit the occasion or weather.
- Match the formality and any weather hints in the description.
- Prefer colours, materials, and styles that go well together.
- Only ever use item ids that appear in the wardrobe. Never invent items.
- If the wardrobe can't reasonably cover the request, pick the closest fit and say so.

Return the chosen item ids and one or two sentences explaining the choice."""

_SCHEMA = {
    "type": "object",
    "properties": {
        "item_ids": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
    },
    "required": ["item_ids", "rationale"],
    "additionalProperties": False,
}


class StylistUnavailable(RuntimeError):
    """The stylist could not produce a suggestion (no API key, upstream error, ...)."""


def _brief(item: Item) -> dict[str, object]:
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "color": item.color,
        "brand": item.brand,
        "season": item.season,
        "material": item.material,
    }


def suggest_outfit(prompt: str, items: list[Item]) -> tuple[list[str], str]:
    """Return (chosen item ids, rationale). Raises StylistUnavailable on any failure."""
    key = get_settings().anthropic_api_key
    if not key:
        raise StylistUnavailable("AI suggestions aren't set up yet (no ANTHROPIC_API_KEY).")
    if not items:
        raise StylistUnavailable("Your wardrobe is empty — add a few items first.")

    wardrobe = json.dumps([_brief(i) for i in items[:_MAX_ITEMS]], indent=2)
    user = f"Wardrobe:\n{wardrobe}\n\nToday's plan: {prompt.strip()}"

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
        raise StylistUnavailable(f"The stylist service is unavailable right now ({exc}).") from exc

    text = next((b.text for b in response.content if b.type == "text"), "")
    try:
        data = json.loads(text)
        return [str(i) for i in data["item_ids"]], str(data["rationale"])
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise StylistUnavailable("The stylist returned an unexpected response.") from exc
