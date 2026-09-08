from fastapi.testclient import TestClient

AUTH = ("me", "change-me")


def _item(client: TestClient, name: str, category: str = "top") -> str:
    return client.post(
        "/api/items", json={"name": name, "category": category}, auth=AUTH
    ).json()["id"]


def test_outfits_require_auth(client: TestClient) -> None:
    assert client.get("/api/outfits").status_code == 401


def test_outfit_crud(client: TestClient) -> None:
    a = _item(client, "White Tee")
    b = _item(client, "Blue Jeans", "bottom")

    created = client.post(
        "/api/outfits",
        json={"name": "Casual Friday", "occasion": "work", "item_ids": [a, b]},
        auth=AUTH,
    )
    assert created.status_code == 201, created.text
    outfit = created.json()
    assert outfit["name"] == "Casual Friday"
    assert {i["id"] for i in outfit["items"]} == {a, b}
    outfit_id = outfit["id"]

    listed = client.get("/api/outfits", auth=AUTH)
    assert [o["id"] for o in listed.json()] == [outfit_id]

    # replace the item set and rename
    patched = client.patch(
        f"/api/outfits/{outfit_id}",
        json={"name": "Friday Fit", "item_ids": [a]},
        auth=AUTH,
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Friday Fit"
    assert [i["id"] for i in patched.json()["items"]] == [a]

    assert client.delete(f"/api/outfits/{outfit_id}", auth=AUTH).status_code == 204
    assert client.get(f"/api/outfits/{outfit_id}", auth=AUTH).status_code == 404


def test_unknown_item_ids_are_ignored(client: TestClient) -> None:
    a = _item(client, "Sweater")
    resp = client.post(
        "/api/outfits",
        json={"name": "Mixed", "item_ids": [a, "does-not-exist"]},
        auth=AUTH,
    )
    assert resp.status_code == 201
    assert [i["id"] for i in resp.json()["items"]] == [a]


def test_deleting_an_item_removes_it_from_outfits(client: TestClient) -> None:
    a = _item(client, "Jacket", "outerwear")
    b = _item(client, "Boots", "shoes")
    outfit_id = client.post(
        "/api/outfits", json={"name": "Rainy Day", "item_ids": [a, b]}, auth=AUTH
    ).json()["id"]

    assert client.delete(f"/api/items/{a}", auth=AUTH).status_code == 204

    remaining = client.get(f"/api/outfits/{outfit_id}", auth=AUTH)
    assert remaining.status_code == 200
    assert [i["id"] for i in remaining.json()["items"]] == [b]
