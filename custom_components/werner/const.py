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
# Selbstbestimmung: Werner passt erst auf, wenn der Bewohner selbst zugestimmt hat.
CONF_CONSENT = "consent"
CONF_CREATED_BY = "created_by"
SOURCE_UI = "werner_ui"

# Optionen (vom Helfer im Options-Flow)
CONF_SOURCES = "activity_sources"
CONF_BASELOAD = "baseload_w"
# Adresse der Signal-Messenger-App, z. B. http://<app>:8080 (leer: automatisch suchen)
CONF_SIGNAL_URL = "signal_url"
DEFAULT_BASELOAD = 300

# Optionen für Energie und Auto (alle freiwillig)
CONF_WEATHER = "weather"
CONF_GRID_POWER = "grid_power"
CONF_GRID_ENERGY = "grid_energy"
CONF_PV_POWER = "pv_power"
CONF_BATTERY_SOC = "battery_soc"
CONF_PV_KWP = "pv_kwp"
CONF_VEHICLE_NAME = "vehicle_name"
CONF_VEHICLE_SOC = "vehicle_soc"
CONF_CHARGE_MODE = "charge_mode"
# Diagramme: Strompreis (Nord Pool), Sonnen-Vorhersage (Forecast.Solar)
CONF_PRICE_ENTRY = "price_entry"
CONF_PRICE_MARKUP = "price_markup_ct"
CONF_PRICE_VAT = "price_vat"
CONF_PV_FORECAST = "pv_forecast"
ENERGY_ENTITY_KEYS = (
    CONF_WEATHER,
    CONF_GRID_POWER,
    CONF_GRID_ENERGY,
    CONF_PV_POWER,
    CONF_BATTERY_SOC,
    CONF_VEHICLE_SOC,
    CONF_CHARGE_MODE,
)

# Oberfläche „Mein Zuhause“ (Panel in der Seitenleiste und Karte für Dashboards)
FRONTEND_URL_BASE = "/werner_static"
FRONTEND_FILE = "werner-mein-zuhause.js"
PANEL_URL_PATH = "werner"
PANEL_TITLE = "Mein Zuhause"
PANEL_ICON = "mdi:home-heart"
WEBCOMPONENT = "werner-mein-zuhause"

# Dienste
SERVICE_TEST_PERSON = "test_person"
SERVICE_ASK = "ask"
ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_PERSON = "person"
ATTR_REASON = "reason"

# Aktivität einer Quelle höchstens so oft ins Protokoll schreiben
ACTIVITY_LOG_MINUTES = 30

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
    # Kamera und Mikrofon nur mit Zustimmung des Bewohners (standardmäßig aus)
    "consent_camera": False,
    "consent_microphone": False,
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
