"""E-Mail an Vertrauenspersonen – über ein eigenes Postfach nur für Werner.

Die Zugangsdaten gelten für den ganzen Haushalt und werden einmal von einem
Helfer (Administrator) eingetragen. Sie liegen im Speicher von Home Assistant
(.storage/werner.mail) und nicht in einer Entität, damit sie nicht im Verlauf
oder in der Oberfläche auftauchen.

Wer die E-Mail bekommt, kann mit einem Klick antworten („Ich kümmere mich“,
„Fehlalarm“, „Kann nicht“) – sofern Home Assistant von außen erreichbar ist.
"""

from __future__ import annotations

from collections.abc import Callable
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
import html
import secrets
import smtplib
import ssl
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import DOMAIN

STORAGE_KEY = f"{DOMAIN}.mail"
STORAGE_VERSION = 1
SECURITY_STARTTLS = "starttls"
SECURITY_SSL = "ssl"
FIELDS = ("server", "port", "security", "user", "password", "sender_name")
DEFAULT_SENDER_NAME = "Werner"


class MailError(Exception):
    """Fehler beim Versand – mit einem Satz, den man in der Oberfläche zeigen kann."""


class WernerMail:
    """Einstellungen und Versand für den ganzen Haushalt."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.settings: dict[str, Any] = {}
        self._loaded = False

    async def async_load(self) -> None:
        if not self._loaded:
            self.settings = (await self._store.async_load()) or {}
            self._loaded = True

    @property
    def configured(self) -> bool:
        s = self.settings
        return bool(s.get("server") and s.get("user") and s.get("password"))

    def public(self) -> dict[str, Any]:
        """Einstellungen ohne Passwort – für die Oberfläche."""
        s = self.settings
        return {
            "configured": self.configured,
            "server": s.get("server", ""),
            "port": s.get("port", 587),
            "security": s.get("security", SECURITY_STARTTLS),
            "user": s.get("user", ""),
            "sender_name": s.get("sender_name", DEFAULT_SENDER_NAME),
            "has_password": bool(s.get("password")),
        }

    async def async_save(self, values: dict[str, Any]) -> None:
        """Speichern. Ein leeres Passwort behält das bisherige."""
        await self.async_load()
        new = {**self.settings}
        for key in FIELDS:
            if key not in values:
                continue
            value = values[key]
            if key == "password" and not value:
                continue
            new[key] = value.strip() if isinstance(value, str) and key != "password" else value
        self.settings = new
        await self._store.async_save(new)

    async def async_send(self, to: str, subject: str, text: str, html_body: str | None = None) -> None:
        """E-Mail senden. Wirft MailError mit einer verständlichen Meldung."""
        await self.async_load()
        if not self.configured:
            raise MailError("Der E-Mail-Versand ist noch nicht eingerichtet. Das macht ein Helfer.")
        if not to or "@" not in to:
            raise MailError("Diese E-Mail-Adresse stimmt nicht.")
        await self.hass.async_add_executor_job(self._send, dict(self.settings), to, subject, text, html_body)

    @staticmethod
    def _send(s: dict[str, Any], to: str, subject: str, text: str, html_body: str | None) -> None:
        user = s["user"]
        msg = EmailMessage()
        msg["From"] = formataddr((s.get("sender_name") or DEFAULT_SENDER_NAME, user))
        msg["To"] = to
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain=user.split("@")[-1] if "@" in user else None)
        msg.set_content(text)
        if html_body:
            msg.add_alternative(html_body, subtype="html")
        try:
            port = int(s.get("port") or 587)
        except (TypeError, ValueError):
            port = 587
        ctx = ssl.create_default_context()
        try:
            if s.get("security") == SECURITY_SSL or port == 465:
                with smtplib.SMTP_SSL(s["server"], port, context=ctx, timeout=30) as smtp:
                    smtp.login(user, s["password"])
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(s["server"], port, timeout=30) as smtp:
                    smtp.ehlo()
                    smtp.starttls(context=ctx)
                    smtp.ehlo()
                    smtp.login(user, s["password"])
                    smtp.send_message(msg)
        except smtplib.SMTPAuthenticationError as err:
            raise MailError(
                "Anmeldung beim Postfach abgelehnt. Stimmen Benutzer und Passwort? "
                "Bei GMX und WEB.DE den SMTP-Zugriff erlauben, bei Gmail ein App-Passwort nehmen."
            ) from err
        except (OSError, smtplib.SMTPException) as err:
            raise MailError(f"Versand fehlgeschlagen: {str(err)[:160]}") from err


def get_mail(hass: HomeAssistant) -> WernerMail:
    """Ein gemeinsames Objekt für alle Bewohner."""
    data = hass.data.setdefault(DOMAIN, {})
    if "mail" not in data:
        data["mail"] = WernerMail(hass)
    return data["mail"]


# --------------------------------------------------------------- Antwort per Klick


def answer_page(text: str, button: str | None = None) -> str:
    """Kleine Seite nach einem Klick in der E-Mail – mit Knopf zum Bestätigen.

    Erst der Knopf (POST) zählt. So lösen Virenscanner, die Links in E-Mails
    vorab öffnen, keine Antwort aus.
    """
    form = (
        "<form method='post'><button type='submit' style='font-size:20px;font-weight:700;"
        "min-height:56px;width:100%;border:none;border-radius:14px;background:#1F4E79;color:#fff'>"
        f"{html.escape(button)}</button></form>"
        if button
        else ""
    )
    return (
        "<!DOCTYPE html><html lang='de'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'><title>Werner</title></head>"
        "<body style=\"font-family:system-ui,sans-serif;background:#F5F2EA;color:#1E2421;"
        "display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0\">"
        "<div style='background:#fff;border:1px solid #E2DDD1;border-radius:18px;padding:28px;"
        f"max-width:420px;font-size:20px;line-height:1.4'><b>Werner</b><p>{html.escape(text)}</p>{form}</div>"
        "</body></html>"
    )


@callback
def async_register_answers(
    hass: HomeAssistant, on_answer: Callable[[str], None]
) -> tuple[dict[str, str], Callable[[], None]]:
    """Drei Einmal-Links anlegen. Ergebnis: Links je Antwort (leer ohne Adresse von außen)."""
    from aiohttp import web  # noqa: PLC0415

    from homeassistant.components import webhook  # noqa: PLC0415
    from homeassistant.helpers.network import NoURLAvailableError, get_url  # noqa: PLC0415

    if "webhook" not in hass.config.components:
        return {}, lambda: None
    try:
        base = get_url(hass, allow_internal=False, prefer_external=True)
    except NoURLAvailableError:
        return {}, lambda: None

    thanks = {
        "take": "Danke! Werner hat notiert, dass Sie sich kümmern.",
        "false_alarm": "Danke! Werner hat notiert: Fehlalarm, alles gut.",
        "next": "Danke! Werner informiert jetzt die nächste Person.",
    }
    confirm = {
        "take": ("Sie kümmern sich?", "Ja, ich kümmere mich"),
        "false_alarm": ("Es ist ein Fehlalarm?", "Ja, Fehlalarm"),
        "next": ("Sie können gerade nicht?", "Nächste Person informieren"),
    }
    ids: dict[str, str] = {}
    links: dict[str, str] = {}
    for answer in thanks:
        webhook_id = f"werner_{secrets.token_urlsafe(24)}"
        ids[answer] = webhook_id

        async def _handle(_hass: HomeAssistant, _id: str, request: Any, answer: str = answer) -> web.Response:
            if request.method != "POST":
                question, button = confirm[answer]
                return web.Response(text=answer_page(question, button), content_type="text/html")
            on_answer(answer)
            return web.Response(text=answer_page(thanks[answer]), content_type="text/html")

        webhook.async_register(
            hass, DOMAIN, "Werner Antwort", webhook_id, _handle,
            local_only=False, allowed_methods=("GET", "POST"),
        )
        links[answer] = f"{base}/api/webhook/{webhook_id}"

    @callback
    def _unregister() -> None:
        for webhook_id in ids.values():
            webhook.async_unregister(hass, webhook_id)

    return links, _unregister
