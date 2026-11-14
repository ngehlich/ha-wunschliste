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


async def test_self_reserve_public(hass: HomeAssistant, hass_ws_client, hass_client_no_auth) -> None:
    await _setup(hass)
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "wunschliste/item_save", "item": {"name": "Spieluhr", "price": 30, "theme": "Spielen"}})
    item = (await ws.receive_json())["result"]["item"]
    await ws.send_json({"id": 2, "type": "wunschliste/item_save", "item": {"name": "Essen kochen", "price": 0}})
    zeit = (await ws.receive_json())["result"]["item"]

    events = []
    hass.bus.async_listen("wunschliste_vergeben", events.append)
    hass.bus.async_listen("wunschliste_freigegeben", events.append)
    client = await hass_client_no_auth()

    # Ohne Namen, unbekannter Wunsch, Zeit-Idee: abgelehnt
    r = await client.post("/api/wunschliste/vergeben", json={"id": item["id"], "name": "  "})
    assert r.status == 400
    r = await client.post("/api/wunschliste/vergeben", json={"id": "gibtsnicht", "name": "Anna"})
    assert r.status == 404
    r = await client.post("/api/wunschliste/vergeben", json={"id": zeit["id"], "name": "Anna"})
    assert r.status == 400

    r = await client.post("/api/wunschliste/vergeben", json={"id": item["id"], "name": " Tante Anna "})
    assert r.status == 200
    key = (await r.json())["key"]
    await hass.async_block_till_done()
    assert events[-1].data == {"id": item["id"], "wunsch": "Spieluhr", "von": "Tante Anna"}

    # Öffentlich vergeben, aber ohne Namen und ohne Schlüssel
    r = await client.get("/api/wunschliste/liste")
    text = await r.text()
    assert "Tante Anna" not in text and key not in text
    pub = await r.json()
    assert next(i for i in pub["items"] if i["id"] == item["id"])["taken"] is True

    # Zweites Markieren geht nicht
    r = await client.post("/api/wunschliste/vergeben", json={"id": item["id"], "name": "Onkel Bob"})
    assert r.status == 409

    # Im Bearbeiten-Menü: Name sichtbar, Schlüssel nicht
    await ws.send_json({"id": 3, "type": "wunschliste/get"})
    got = next(i for i in (await ws.receive_json())["result"]["items"] if i["id"] == item["id"])
    assert got["reservedBy"] == "Tante Anna"
    assert got["selfReserved"] is True
    assert "reservedKey" not in got

    # Bearbeiten im Menü behält die Selbst-Markierung
    await ws.send_json({"id": 4, "type": "wunschliste/item_save", "item": {**got, "note": "blau"}})
    assert (await ws.receive_json())["result"]["item"]["selfReserved"] is True

    # Freigeben nur mit richtigem Schlüssel
    r = await client.post("/api/wunschliste/freigeben", json={"id": item["id"], "key": "x" * 32})
    assert r.status == 403
    r = await client.post("/api/wunschliste/freigeben", json={"id": item["id"], "key": key})
    assert r.status == 200
    await hass.async_block_till_done()
    assert events[-1].event_type == "wunschliste_freigegeben"
    await ws.send_json({"id": 5, "type": "wunschliste/get"})
    got = next(i for i in (await ws.receive_json())["result"]["items"] if i["id"] == item["id"])
    assert got["reservedBy"] == "" and got["selfReserved"] is False

    # Vom Menü vergeben -> öffentlich nicht freigebbar
    await ws.send_json({"id": 6, "type": "wunschliste/item_save", "item": {**got, "reservedBy": "Oma"}})
    assert (await ws.receive_json())["success"]
    r = await client.post("/api/wunschliste/freigeben", json={"id": item["id"], "key": key})
    assert r.status == 403


async def test_public_rate_limit(hass: HomeAssistant, hass_client_no_auth) -> None:
    await _setup(hass)
    client = await hass_client_no_auth()
    codes = [(await client.post("/api/wunschliste/vergeben", json={"id": "x", "name": "a"})).status for _ in range(22)]
    assert codes[:20] == [404] * 20
    assert codes[-1] == 429


async def test_old_howto_is_updated(hass: HomeAssistant, hass_storage) -> None:
    from custom_components.wunschliste import DEFAULT_SETTINGS, OLD_HOWTO
    hass_storage["wunschliste"] = {"version": 1, "key": "wunschliste", "data": {
        "rev": 3, "settings": {"howto": OLD_HOWTO, "title": "Liste"}, "items": []}}
    await _setup(hass)
    assert hass.data["wunschliste"].settings["howto"] == DEFAULT_SETTINGS["howto"]
    assert hass.data["wunschliste"].settings["title"] == "Liste"
