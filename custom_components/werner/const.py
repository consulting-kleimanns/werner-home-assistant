"""Konstanten für Werner."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "werner"

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]

# Einrichtung (config entry data)
CONF_NAME = "name"
CONF_PERSON = "person"
CONF_NOTIFY = "notify_service"

# Optionen (vom Helfer im Options-Flow)
CONF_SOURCES = "activity_sources"
CONF_BASELOAD = "baseload_w"
DEFAULT_BASELOAD = 300

# Status (Schlüssel; Texte über Übersetzungen)
STATUS_OK = "ok"
STATUS_ASKING = "asking"
STATUS_INFORMED = "informed"
STATUS_HELP = "help"
STATUS_PAUSED = "paused"
STATUSES = [STATUS_OK, STATUS_ASKING, STATUS_INFORMED, STATUS_HELP, STATUS_PAUSED]

# Wege zu den Vertrauenspersonen
WAY_OFF = "off"
WAY_APP = "ha_app"
WAY_SIGNAL = "signal"
WAY_MAIL = "e_mail"
WAYS = [WAY_OFF, WAY_APP, WAY_SIGNAL, WAY_MAIL]

PERSON_COUNT = 3
PERSON_FIELDS = ("name", "contact", "phone", "e_mail")

# Einstellungen je Bewohner und ihre Standardwerte
DEFAULT_SETTINGS: dict[str, object] = {
    "paused": False,
    "rule_morning": True,
    "rule_quiet": True,
    "rule_night": True,
    "morning_until": 10,
    "quiet_hours": 4,
    "wait_minutes": 10,
}
for _n in range(1, PERSON_COUNT + 1):
    for _f in PERSON_FIELDS:
        DEFAULT_SETTINGS[f"person_{_n}_{_f}"] = ""
    DEFAULT_SETTINGS[f"person_{_n}_way"] = WAY_OFF

# Zeiten
CONTACT_WAIT_MINUTES = 15
CHECK_INTERVAL_MINUTES = 10
NIGHT_START_HOUR = 0
NIGHT_END_HOUR = 5
MORNING_FROM_HOUR = 5
MORNING_LATEST_HOUR = 13
DAY_START_HOUR = 8
DAY_END_HOUR = 22

# Benachrichtigungen der Home-Assistant-App
EVENT_NOTIFICATION_ACTION = "mobile_app_notification_action"
ACTION_OK = "WERNER_OK"
ACTION_HELP = "WERNER_HILFE"
ACTION_TAKE = "WERNER_KUEMMERE"
ACTION_FALSE_ALARM = "WERNER_FEHLALARM"
ACTION_NEXT = "WERNER_NAECHSTE"


def signal_update(entry_id: str) -> str:
    """Dispatcher-Signal, wenn sich Zustand oder Einstellungen eines Bewohners ändern."""
    return f"{DOMAIN}_{entry_id}_update"
