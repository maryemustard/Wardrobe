from fastapi.testclient import TestClient

AUTH = ("me", "change-me")  # matches Settings defaults used in tests


def test_items_require_auth(client: TestClient) -> None:
    assert client.get("/api/items").status_code == 401


def test_item_crud(client: TestClient) -> None:
    created = client.post(
        "/api/items",
        json={"name": "Blue Jeans", "category": "bottom", "brand": "Levi's"},
        auth=AUTH,
    )
    assert created.status_code == 201, created.text
    item = created.json()
    assert item["name"] == "Blue Jeans"
    assert item["is_archived"] is False
    item_id = item["id"]

    listed = client.get("/api/items", auth=AUTH)
    assert listed.status_code == 200
    assert [i["id"] for i in listed.json()] == [item_id]

    fetched = client.get(f"/api/items/{item_id}", auth=AUTH)
    assert fetched.status_code == 200

    updated = client.patch(f"/api/items/{item_id}", json={"color": "indigo"}, auth=AUTH)
    assert updated.status_code == 200
    assert updated.json()["color"] == "indigo"

    deleted = client.delete(f"/api/items/{item_id}", auth=AUTH)
    assert deleted.status_code == 204
    assert client.get(f"/api/items/{item_id}", auth=AUTH).status_code == 404


def test_list_filters(client: TestClient) -> None:
    client.post("/api/items", json={"name": "Tee", "category": "top"}, auth=AUTH)
    client.post("/api/items", json={"name": "Boots", "category": "shoes"}, auth=AUTH)

    tops = client.get("/api/items", params={"category": "top"}, auth=AUTH)
    assert [i["name"] for i in tops.json()] == ["Tee"]

    search = client.get("/api/items", params={"q": "boot"}, auth=AUTH)
    assert [i["name"] for i in search.json()] == ["Boots"]


def test_archived_hidden_by_default(client: TestClient) -> None:
    created = client.post(
        "/api/items", json={"name": "Old Coat", "category": "outerwear"}, auth=AUTH
    )
    item_id = created.json()["id"]
    client.patch(f"/api/items/{item_id}", json={"is_archived": True}, auth=AUTH)

    assert client.get("/api/items", auth=AUTH).json() == []
    archived = client.get("/api/items", params={"archived": True}, auth=AUTH)
    assert [i["id"] for i in archived.json()] == [item_id]


def test_bad_category_rejected(client: TestClient) -> None:
    resp = client.post("/api/items", json={"name": "Thing", "category": "hat"}, auth=AUTH)
    assert resp.status_code == 422


def _make_item(client: TestClient) -> str:
    created = client.post("/api/items", json={"name": "Tee", "category": "top"}, auth=AUTH)
    return created.json()["id"]


def test_image_upload_and_remove(client: TestClient) -> None:
    item_id = _make_item(client)

    up = client.post(
        f"/api/items/{item_id}/image",
        files={"file": ("photo.png", b"\x89PNG\r\n\x1a\n fake bytes", "image/png")},
        auth=AUTH,
    )
    assert up.status_code == 200, up.text
    assert up.json()["image_url"] == f"/media/{item_id}.png"
    assert up.json()["image_public_id"] == f"{item_id}.png"

    rm = client.delete(f"/api/items/{item_id}/image", auth=AUTH)
    assert rm.status_code == 200
    assert rm.json()["image_url"] is None
    assert rm.json()["image_public_id"] is None


def test_image_rejects_non_image(client: TestClient) -> None:
    item_id = _make_item(client)
    resp = client.post(
        f"/api/items/{item_id}/image",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        auth=AUTH,
    )
    assert resp.status_code == 415


def test_delete_item_removes_its_image(client: TestClient) -> None:
    item_id = _make_item(client)
    client.post(
        f"/api/items/{item_id}/image",
        files={"file": ("p.png", b"x", "image/png")},
        auth=AUTH,
    )
    assert client.delete(f"/api/items/{item_id}", auth=AUTH).status_code == 204
