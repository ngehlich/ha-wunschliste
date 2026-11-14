"""Wunschliste: Geschenkliste zur Geburt, gepflegt in Home Assistant.

Die Daten liegen nur in Home Assistant (/config/.storage/wunschliste, Teil jeder
Sicherung). Bearbeitet wird über den Menüpunkt „Wunschliste“ in der Seitenleiste,
der durch den Home-Assistant-Login geschützt ist.

Für Familie und Freunde gibt es eine Nur-Lese-Seite ohne Login unter /geschenkliste.
Sie bekommt nur die öffentlichen Felder: wer etwas schenkt, sieht dort niemand,
nur dass es vergeben ist.
"""
from __future__ import annotations

import asyncio
import logging
import re
import secrets
from datetime import date
from pathlib import Path
from typing import Any

import voluptuous as vol
from aiohttp import web

from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import HomeAssistantView, StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

DOMAIN = "wunschliste"
VERSION = "1.0.0"
STORAGE_VERSION = 1
PANEL_URL = "wunschliste"
STATIC_URL = "/wunschliste_static/wunschliste-panel.js"
PANEL_FILE = Path(__file__).parent / "wunschliste-panel.js"
PUBLIC_FILE = Path(__file__).parent / "public.html"
PUBLIC_PAGE_URL = "/geschenkliste"
PUBLIC_DATA_URL = "/api/wunschliste/liste"
SIGNAL = f"{DOMAIN}_changed"
REGISTERED = f"{DOMAIN}_registered"
MAX_ITEMS = 500

THEMES = [
    "Pflege", "Schlafen", "Essen", "Baden", "Spielen", "Kleidung",
    "Unterwegs", "Gesundheit", "Zeit & Gutscheine", "Sonstiges",
]
PUBLIC_FIELDS = ("id", "name", "note", "price", "theme", "shop", "url")

DEFAULT_SETTINGS: dict[str, Any] = {
    "title": "Unsere Wunschliste",
    "etDate": "",
    "sizes": "",
    "intro": (
        "Viele von euch haben gefragt, worüber wir uns freuen. Hier ist unsere "
        "Liste, von Kleinigkeiten bis zu größeren Sachen. Nichts davon ist Pflicht, "
        "und über Zeit statt Zeug freuen wir uns genauso."
    ),
    "howto": (
        "So geht’s: Such dir etwas aus, das noch frei ist, und sag uns kurz "
        "Bescheid. Wir markieren es dann als vergeben, damit nichts doppelt kommt. "
        "Die Links sind Vorschläge, kauft gern, wo ihr wollt."
    ),
}


def _text(max_len: int) -> Any:
    return vol.All(vol.Coerce(str), vol.Strip, vol.Length(max=max_len))


def _url(value: Any) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    if not re.match(r"^https?://", value, re.I):
        if re.match(r"^[a-z][a-z0-9+.-]*:", value, re.I):
            raise vol.Invalid("nur http- und https-Links")
        value = "https://" + value
    if len(value) > 2000 or any(c in value for c in " \n\r\t<>\"'"):
        raise vol.Invalid("ungültiger Link")
    return value


def _price(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    num = float(value)
    if num < 0 or num > 100000:
        raise vol.Invalid("ungültiger Preis")
    return round(num, 2)


def _iso_date(value: Any) -> str:
    value = str(value or "").strip()
    if value:
        date.fromisoformat(value)
    return value


ITEM_SCHEMA = vol.Schema(
    {
        vol.Optional("id"): vol.All(str, vol.Match(r"^[A-Za-z0-9_-]{1,40}$")),
        vol.Required("name"): vol.All(vol.Coerce(str), vol.Strip, vol.Length(min=1, max=200)),
        vol.Optional("note", default=""): _text(500),
        vol.Optional("price", default=0): _price,
        vol.Optional("theme", default="Sonstiges"): vol.In(THEMES),
        vol.Optional("shop", default=""): _text(80),
        vol.Optional("url", default=""): _url,
        vol.Optional("reservedBy", default=""): _text(100),
    },
    extra=vol.REMOVE_EXTRA,
)

SETTINGS_SCHEMA = vol.Schema(
    {
        vol.Optional("title"): _text(120),
        vol.Optional("etDate"): _iso_date,
        vol.Optional("sizes"): _text(40),
        vol.Optional("intro"): _text(1000),
        vol.Optional("howto"): _text(1000),
    },
    extra=vol.REMOVE_EXTRA,
)


def _new_id() -> str:
    return "w" + secrets.token_hex(5)


class WishStore:
    """Einstellungen und Wünsche, gespeichert in .storage."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, DOMAIN, private=True, atomic_writes=True
        )
        self.lock = asyncio.Lock()
        self.rev = 0
        self.settings: dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.items: list[dict[str, Any]] = []

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if data:
            self.rev = int(data.get("rev", 0))
            self.settings = {**DEFAULT_SETTINGS, **data.get("settings", {})}
            self.items = list(data.get("items", []))

    async def async_save(self) -> None:
        self.rev += 1
        await self._store.async_save(
            {"rev": self.rev, "settings": self.settings, "items": self.items}
        )

    def full(self) -> dict[str, Any]:
        return {"rev": self.rev, "settings": self.settings, "items": self.items}

    def public(self) -> dict[str, Any]:
        items = []
        for it in self.items:
            pub = {k: it.get(k) for k in PUBLIC_FIELDS}
            pub["taken"] = bool(it.get("reservedBy"))
            items.append(pub)
        return {"settings": self.settings, "items": items}

    def upsert(self, item: dict[str, Any]) -> dict[str, Any]:
        item_id = item.get("id")
        for idx, cur in enumerate(self.items):
            if cur["id"] == item_id:
                self.items[idx] = item
                return item
        if len(self.items) >= MAX_ITEMS:
            raise vol.Invalid("zu viele Wünsche")
        if not item_id or any(i["id"] == item_id for i in self.items):
            item["id"] = _new_id()
        self.items.append(item)
        return item


def _store(hass: HomeAssistant, connection: Any, msg_id: int) -> WishStore | None:
    store: WishStore | None = hass.data.get(DOMAIN)
    if store is None:
        connection.send_error(msg_id, "not_loaded", "Wunschliste ist nicht eingerichtet")
    return store


async def _changed(hass: HomeAssistant, store: WishStore) -> None:
    await store.async_save()
    async_dispatcher_send(hass, SIGNAL, store.rev)


@websocket_api.websocket_command({vol.Required("type"): "wunschliste/get"})
@callback
def ws_get(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (store := _store(hass, connection, msg["id"])) is not None:
        connection.send_result(msg["id"], store.full())


@websocket_api.websocket_command(
    {vol.Required("type"): "wunschliste/item_save", vol.Required("item"): dict}
)
@websocket_api.async_response
async def ws_item_save(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (store := _store(hass, connection, msg["id"])) is None:
        return
    try:
        item = ITEM_SCHEMA(msg["item"])
    except vol.Invalid as err:
        connection.send_error(msg["id"], "invalid", str(err))
        return
    async with store.lock:
        try:
            item = store.upsert(item)
        except vol.Invalid as err:
            connection.send_error(msg["id"], "invalid", str(err))
            return
        await _changed(hass, store)
        connection.send_result(msg["id"], {"item": item, "rev": store.rev})


@websocket_api.websocket_command(
    {vol.Required("type"): "wunschliste/item_delete", vol.Required("item_id"): str}
)
@websocket_api.async_response
async def ws_item_delete(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (store := _store(hass, connection, msg["id"])) is None:
        return
    async with store.lock:
        before = len(store.items)
        store.items = [i for i in store.items if i["id"] != msg["item_id"]]
        if len(store.items) != before:
            await _changed(hass, store)
        connection.send_result(msg["id"], {"rev": store.rev})


@websocket_api.websocket_command(
    {vol.Required("type"): "wunschliste/settings", vol.Required("settings"): dict}
)
@websocket_api.async_response
async def ws_settings(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    if (store := _store(hass, connection, msg["id"])) is None:
        return
    try:
        new = SETTINGS_SCHEMA(msg["settings"])
    except (vol.Invalid, ValueError) as err:
        connection.send_error(msg["id"], "invalid", str(err))
        return
    async with store.lock:
        store.settings = {**store.settings, **new}
        await _changed(hass, store)
        connection.send_result(msg["id"], {"settings": store.settings, "rev": store.rev})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "wunschliste/import",
        vol.Required("data"): dict,
        vol.Optional("replace", default=False): bool,
    }
)
@websocket_api.async_response
async def ws_import(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Liste aus einer JSON-Datei übernehmen (Format wie Export)."""
    if (store := _store(hass, connection, msg["id"])) is None:
        return
    data = msg["data"]
    raw_items = data.get("items")
    if not isinstance(raw_items, list) or len(raw_items) > MAX_ITEMS:
        connection.send_error(msg["id"], "invalid", "Keine gültige Liste gefunden")
        return
    try:
        items = [ITEM_SCHEMA(i) for i in raw_items]
        settings = dict(data.get("settings") or {})
        if data.get("etDate") and "etDate" not in settings:  # älteres Format
            settings["etDate"] = data["etDate"]
        settings = SETTINGS_SCHEMA(settings)
    except (vol.Invalid, ValueError, TypeError) as err:
        connection.send_error(msg["id"], "invalid", f"Datei passt nicht: {err}")
        return
    async with store.lock:
        if msg["replace"]:
            store.items = []
        added = 0
        for item in items:
            try:
                store.upsert(item)
            except vol.Invalid:
                break
            added += 1
        store.settings = {**store.settings, **settings}
        await _changed(hass, store)
        connection.send_result(msg["id"], {"count": added, "rev": store.rev})


@websocket_api.websocket_command({vol.Required("type"): "wunschliste/subscribe"})
@callback
def ws_subscribe(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Meldet Änderungen, damit andere offene Geräte sofort nachladen."""

    @callback
    def forward(rev: int) -> None:
        connection.send_message(websocket_api.event_message(msg["id"], {"rev": rev}))

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(hass, SIGNAL, forward)
    connection.send_result(msg["id"])


NO_STORE = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"}


class PublicPageView(HomeAssistantView):
    """Öffentliche Nur-Lese-Seite, ohne Login."""

    url = PUBLIC_PAGE_URL
    extra_urls = ["/api/wunschliste/seite"]
    name = "wunschliste:seite"
    requires_auth = False

    def __init__(self, html: str) -> None:
        self._html = html

    async def get(self, request: web.Request) -> web.Response:
        return web.Response(
            text=self._html,
            content_type="text/html",
            charset="utf-8",
            headers={
                **NO_STORE,
                "Content-Security-Policy": (
                    "default-src 'none'; script-src 'unsafe-inline'; "
                    "style-src 'unsafe-inline' https://fonts.googleapis.com; "
                    "font-src https://fonts.gstatic.com; connect-src 'self'; "
                    "img-src data:; base-uri 'none'; form-action 'none'; "
                    "frame-ancestors 'self'"
                ),
                "Referrer-Policy": "no-referrer",
            },
        )


class PublicDataView(HomeAssistantView):
    """Öffentliche Liste als JSON, ohne Namen der Schenkenden."""

    url = PUBLIC_DATA_URL
    name = "wunschliste:liste"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        store: WishStore | None = request.app["hass"].data.get(DOMAIN)
        if store is None:
            return web.json_response({"error": "nicht eingerichtet"}, status=503, headers=NO_STORE)
        return web.json_response(store.public(), headers=NO_STORE)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    store = WishStore(hass)
    await store.async_load()
    hass.data[DOMAIN] = store

    if not hass.data.get(REGISTERED):
        html = await hass.async_add_executor_job(PUBLIC_FILE.read_text, "utf-8")
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(PANEL_FILE), False)]
        )
        hass.http.register_view(PublicPageView(html))
        hass.http.register_view(PublicDataView())
        for cmd in (ws_get, ws_item_save, ws_item_delete, ws_settings, ws_import, ws_subscribe):
            websocket_api.async_register_command(hass, cmd)
        hass.data[REGISTERED] = True

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name="wunschliste-panel",
        frontend_url_path=PANEL_URL,
        module_url=f"{STATIC_URL}?v={VERSION}",
        sidebar_title="Wunschliste",
        sidebar_icon="mdi:gift-outline",
        embed_iframe=True,
        require_admin=False,
        config={"version": VERSION, "public_path": PUBLIC_PAGE_URL},
    )
    _LOGGER.debug("Wunschliste geladen: %s Wünsche", len(store.items))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    frontend.async_remove_panel(hass, PANEL_URL)
    hass.data.pop(DOMAIN, None)
    return True
