"""Signal für Werner – über die Signal-Messenger-App (signal-cli-rest-api).

Werner nutzt ein Signal-Konto, das als „verknüpftes Gerät“ mit dem Handy eines
Bewohners verbunden wird. Darüber schreibt Werner den Vertrauenspersonen und
liest ihre Antworten 1, 2 oder 3. Alles läuft lokal über die App im Haus.

Die App muss im Modus „json-rpc“ laufen; dann kommen Antworten über einen
Websocket. Im Modus „normal“ fragt Werner alle paar Sekunden nach.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import contextlib
import logging
import re
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_SIGNAL_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SIGNAL = "signal"
POLL_SECONDS = 5
RECONNECT_SECONDS = 30

type ReplyCallback = Callable[[str, str], None]


def normalize_number(number: str, country: str = "+49") -> str:
    """+49 170 0000000, 0170/0000000 und 0049… werden zu +491700000000."""
    raw = re.sub(r"[^\d+]", "", number or "")
    if raw.startswith("00"):
        raw = "+" + raw[2:]
    elif raw.startswith("0"):
        raw = country + raw[1:]
    return raw


def get_client(hass: HomeAssistant) -> SignalClient:
    """Ein gemeinsamer Signal-Zugang für alle Bewohner des Haushalts."""
    data = hass.data.setdefault(DOMAIN, {})
    if DATA_SIGNAL not in data:
        data[DATA_SIGNAL] = SignalClient(hass)
    return data[DATA_SIGNAL]


class SignalClient:
    """Spricht mit der Signal-Messenger-App."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._url: str | None = None
        self._listeners: list[ReplyCallback] = []
        self._task: asyncio.Task | None = None
        self._account: str | None = None

    # ------------------------------------------------------------ Adresse

    def _configured_url(self) -> str | None:
        entries: list[ConfigEntry] = self.hass.config_entries.async_entries(DOMAIN)
        for entry in entries:
            if url := (entry.options.get(CONF_SIGNAL_URL) or "").strip():
                return url.rstrip("/")
        return None

    async def async_url(self) -> str | None:
        """Adresse der App: eingetragen oder unter den installierten Apps gefunden."""
        if url := self._configured_url():
            return url
        if self._url:
            return self._url
        if "hassio" not in self.hass.config.components:
            return None
        try:
            from homeassistant.components.hassio import get_addons_info  # noqa: PLC0415

            addons = get_addons_info(self.hass) or {}
        except Exception:  # noqa: BLE001 – ohne Supervisor gibt es keine Suche
            return None
        for slug in addons:
            if "signal" in slug and "messenger" in slug:
                self._url = f"http://{slug.replace('_', '-')}:8080"
                return self._url
        return None

    # ------------------------------------------------------------ Anfragen

    async def _request(self, method: str, path: str, **kwargs: Any) -> aiohttp.ClientResponse:
        url = await self.async_url()
        if not url:
            raise SignalError("Die Signal-App ist nicht installiert oder nicht eingetragen.")
        session = async_get_clientsession(self.hass)
        timeout = aiohttp.ClientTimeout(total=kwargs.pop("timeout", 30))
        try:
            return await session.request(method, url + path, timeout=timeout, **kwargs)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise SignalError(f"Die Signal-App antwortet nicht ({err}).") from err

    async def async_accounts(self) -> list[str]:
        """Verbundene Signal-Konten (Telefonnummern)."""
        resp = await self._request("GET", "/v1/accounts", timeout=15)
        if resp.status != 200:
            raise SignalError(f"Die Signal-App meldet einen Fehler ({resp.status}).")
        accounts = await resp.json()
        return [a for a in accounts if isinstance(a, str)]

    async def async_account(self) -> str | None:
        accounts = await self.async_accounts()
        self._account = accounts[0] if accounts else None
        if self._account and self._listeners:
            self._ensure_receiver()
        return self._account

    async def async_qr(self) -> bytes:
        """QR-Code (PNG), mit dem das Handy Werner als Gerät verknüpft."""
        resp = await self._request("GET", "/v1/qrcodelink", params={"device_name": "Werner"}, timeout=60)
        if resp.status != 200 or not resp.content_type.startswith("image/"):
            raise SignalError("Der Code konnte nicht erstellt werden. Läuft die App im Modus json-rpc?")
        return await resp.read()

    async def async_send(self, recipient: str, message: str) -> None:
        account = await self.async_account()
        if not account:
            raise SignalError("Signal ist noch nicht mit Werner verbunden.")
        resp = await self._request(
            "POST",
            "/v2/send",
            json={"message": message, "number": account, "recipients": [normalize_number(recipient)]},
        )
        if resp.status not in (200, 201):
            text = (await resp.text())[:200]
            raise SignalError(f"Signal konnte nicht senden ({resp.status}): {text}")

    # ------------------------------------------------------------ Antworten

    @callback
    def async_listen(self, cb: ReplyCallback) -> Callable[[], None]:
        """Antworten empfangen: cb(Absendernummer, Text)."""
        self._listeners.append(cb)
        self._ensure_receiver()

        @callback
        def _remove() -> None:
            if cb in self._listeners:
                self._listeners.remove(cb)
            if not self._listeners and self._task:
                self._task.cancel()
                self._task = None

        return _remove

    @callback
    def _ensure_receiver(self) -> None:
        if self._task is None or self._task.done():
            self._task = self.hass.async_create_background_task(self._receive_loop(), "werner_signal_receive")

    def _dispatch(self, payload: Any) -> None:
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            env = (item or {}).get("envelope") or (item or {}).get("params", {}).get("envelope") or {}
            text = ((env.get("dataMessage") or {}).get("message") or "").strip()
            source = env.get("sourceNumber") or env.get("source") or ""
            if text and source:
                for cb in list(self._listeners):
                    cb(normalize_number(source), text)

    async def _receive_loop(self) -> None:
        while self._listeners:
            try:
                account = self._account or await self.async_account()
                url = await self.async_url()
                if not account or not url:
                    await asyncio.sleep(RECONNECT_SECONDS)
                    continue
                await self._receive_ws(url, account)
            except asyncio.CancelledError:
                raise
            except _UsePolling:
                await self._receive_poll()
            except Exception as err:  # noqa: BLE001 – Verbindung später neu versuchen
                _LOGGER.debug("Signal-Empfang unterbrochen: %s", err)
            await asyncio.sleep(RECONNECT_SECONDS)

    async def _receive_ws(self, url: str, account: str) -> None:
        session = async_get_clientsession(self.hass)
        ws_url = url.replace("http", "ws", 1) + f"/v1/receive/{account}"
        try:
            ws = await session.ws_connect(ws_url, heartbeat=60)
        except aiohttp.WSServerHandshakeError as err:
            raise _UsePolling from err
        async with ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    with contextlib.suppress(ValueError):
                        self._dispatch(msg.json())
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break

    async def _receive_poll(self) -> None:
        while self._listeners and self._account:
            resp = await self._request("GET", f"/v1/receive/{self._account}", timeout=60)
            if resp.status == 200:
                with contextlib.suppress(ValueError, aiohttp.ContentTypeError):
                    self._dispatch(await resp.json())
            await asyncio.sleep(POLL_SECONDS)

    def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None


class SignalError(Exception):
    """Signal ist nicht erreichbar oder nicht verbunden."""


class _UsePolling(Exception):
    """Die App läuft nicht im Modus json-rpc."""
