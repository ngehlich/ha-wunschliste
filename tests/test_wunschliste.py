"""Grundtests: Einrichten, Wünsche pflegen, öffentliche Seite ohne Namen."""
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

DOMAIN = "wunschliste"


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    await async_setup_component(hass, "http", {})
    entry = MockConfigEntry(domain=DOMAIN, title="Wunschliste", data={})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_lifecycle(hass: HomeAssistant, hass_ws_client, hass_client_no_auth) -> None:
    await _setup(hass)
    ws = await hass_ws_client(hass)

    await ws.send_json({"id": 1, "type": "wunschliste/get"})
    res = (await ws.receive_json())["result"]
    assert res["items"] == []
    assert res["settings"]["title"]

    await ws.send_json({"id": 2, "type": "wunschliste/subscribe"})
    assert (await ws.receive_json())["success"]

    await ws.send_json({"id": 3, "type": "wunschliste/item_save", "item": {
        "name": "  Spieluhr  ", "price": "29.9", "theme": "Spielen", "url": "www.example.org/x"}})
    msgs = [await ws.receive_json(), await ws.receive_json()]
    res = next(m for m in msgs if m["id"] == 3)["result"]
    assert any(m["id"] == 2 and m["type"] == "event" for m in msgs)
    item = res["item"]
    assert item["name"] == "Spieluhr"
    assert item["price"] == 29.9
    assert item["url"] == "https://www.example.org/x"
    assert item["id"].startswith("w")

    # Vergeben mit Namen
    await ws.send_json({"id": 4, "type": "wunschliste/item_save", "item": {**item, "reservedBy": "Tante Anna"}})
    msgs = [await ws.receive_json(), await ws.receive_json()]
    assert next(m for m in msgs if m["id"] == 4)["success"]

    # Ungültige Daten werden abgelehnt
    await ws.send_json({"id": 5, "type": "wunschliste/item_save", "item": {"name": "", "price": 1}})
    assert not (await ws.receive_json())["success"]
    await ws.send_json({"id": 6, "type": "wunschliste/item_save", "item": {"name": "x", "url": "javascript:alert(1)"}})
    assert not (await ws.receive_json())["success"]
    await ws.send_json({"id": 7, "type": "wunschliste/item_save", "item": {"name": "x", "theme": "Quatsch"}})
    assert not (await ws.receive_json())["success"]

    await ws.send_json({"id": 8, "type": "wunschliste/settings", "settings": {"etDate": "2026-12-04", "sizes": "Gr. 56–68"}})
    msgs = [await ws.receive_json(), await ws.receive_json()]
    assert next(m for m in msgs if m["id"] == 8)["result"]["settings"]["etDate"] == "2026-12-04"
    await ws.send_json({"id": 9, "type": "wunschliste/settings", "settings": {"etDate": "4.12."}})
    assert not (await ws.receive_json())["success"]

    # Öffentlich: ohne Login, ohne Namen
    client = await hass_client_no_auth()
    r = await client.get("/api/wunschliste/liste")
    assert r.status == 200
    assert r.headers["Cache-Control"] == "no-store"
    pub = await r.json()
    assert pub["items"][0]["taken"] is True
    assert "reservedBy" not in pub["items"][0]
    assert "Tante Anna" not in await r.text()
    assert pub["settings"]["etDate"] == "2026-12-04"

    r = await client.get("/geschenkliste")
    assert r.status == 200
    assert "text/html" in r.headers["Content-Type"]
    assert "/api/wunschliste/liste" in await r.text()

    # Schreiben geht öffentlich nicht
    r = await client.post("/api/wunschliste/liste", json={"items": []})
    assert r.status == 405

    # Import (altes Format mit etDate oben) und Löschen
    await ws.send_json({"id": 10, "type": "wunschliste/import", "replace": False, "data": {
        "etDate": "2026-12-05",
        "items": [{"id": "s2", "name": "Creme", "price": 8, "theme": "Pflege", "shop": "dm", "url": "", "note": "", "reservedBy": ""},
                  {"id": item["id"], "name": "Spieluhr neu", "price": 30, "theme": "Spielen"}]}})
    msgs = [await ws.receive_json(), await ws.receive_json()]
    assert next(m for m in msgs if m["id"] == 10)["result"]["count"] == 2
    await ws.send_json({"id": 11, "type": "wunschliste/get"})
    res = (await ws.receive_json())["result"]
    assert [i["name"] for i in res["items"]] == ["Spieluhr neu", "Creme"]
    assert res["settings"]["etDate"] == "2026-12-05"

    await ws.send_json({"id": 12, "type": "wunschliste/item_delete", "item_id": "s2"})
    msgs = [await ws.receive_json(), await ws.receive_json()]
    assert next(m for m in msgs if m["id"] == 12)["success"]
    await ws.send_json({"id": 13, "type": "wunschliste/import", "replace": True, "data": {"items": "kaputt"}})
    assert not (await ws.receive_json())["success"]
    await ws.send_json({"id": 14, "type": "wunschliste/get"})
    assert len((await ws.receive_json())["result"]["items"]) == 1


async def test_data_survives_reload(hass: HomeAssistant, hass_ws_client) -> None:
    entry = await _setup(hass)
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "wunschliste/item_save", "item": {"name": "Body", "price": 15}})
    assert (await ws.receive_json())["success"]
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    await ws.send_json({"id": 2, "type": "wunschliste/get"})
    assert (await ws.receive_json())["result"]["items"][0]["name"] == "Body"


async def test_config_flow_single(hass: HomeAssistant) -> None:
    r = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert r["type"] == "create_entry"
    r = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert r["type"] == "abort"
