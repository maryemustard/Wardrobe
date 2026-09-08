import pytest
from fastapi.testclient import TestClient

AUTH = ("me", "change-me")


def _item(client: TestClient, name: str, category: str = "top") -> str:
    return client.post(
        "/api/items", json={"name": name, "category": category}, auth=AUTH
    ).json()["id"]


def test_suggest_requires_auth(client: TestClient) -> None:
    assert client.post("/api/outfits/suggest", json={"prompt": "brunch"}).status_code == 401


def test_suggest_without_api_key_returns_503(client: TestClient) -> None:
    _item(client, "Tee")
    resp = client.post("/api/outfits/suggest", json={"prompt": "coffee"}, auth=AUTH)
    assert resp.status_code == 503


def test_suggest_happy_path(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    top = _item(client, "White Tee")
    bottom = _item(client, "Blue Jeans", "bottom")

    def fake_suggest(prompt: str, items: list) -> tuple[list[str], str]:
        return [top, "ghost-id", bottom], "Comfy and neutral for a relaxed day."

    monkeypatch.setattr("app.routers.outfits.suggest_outfit", fake_suggest)

    resp = client.post(
        "/api/outfits/suggest", json={"prompt": "coffee with a friend"}, auth=AUTH
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert [i["id"] for i in body["items"]] == [top, bottom]  # unknown id dropped
    assert "neutral" in body["rationale"]


def test_suggest_rejects_blank_prompt(client: TestClient) -> None:
    resp = client.post("/api/outfits/suggest", json={"prompt": ""}, auth=AUTH)
    assert resp.status_code == 422
