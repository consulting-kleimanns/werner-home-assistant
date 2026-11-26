"""Grundverbrauch: anerkennen statt antreiben (Musterdaten: Erika)."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

from homeassistant.core import HomeAssistant

from custom_components.werner.baseload import FLOOR_W, Grundverbrauch, evaluate, new_wins
from custom_components.werner.const import CONF_GRID_ENERGY

LAST = date(2026, 11, 26)


def _nights(weekly: list[float | None]) -> dict[str, float | None]:
    """Je Woche sieben gleiche Nächte; die letzte Woche endet mit LAST."""
    nights: dict[str, float | None] = {}
    for k, value in enumerate(reversed(weekly)):
        for d in range(7):
            nights[(LAST - timedelta(days=7 * k + d)).isoformat()] = value
    return nights


def test_fortschritt_wird_anerkannt() -> None:
    state = evaluate(_nights([142, 140, 131, 124, 118, 104, 98, 96]), {"w": 142, "date": "x"}, LAST)
    assert state["current_w"] == 96
    assert state["level"] == "good"
    assert state["saved_w"] == 46
    # Nur ein kleiner Schritt: etwa 10 Prozent weniger.
    assert state["goal_w"] == 85
    assert not state["done"] and state["rise"] is None
    assert set(new_wins(state, {"w": 142, "date": "x"}, {})) == {"minus_10", "good"}


def test_sehr_gut_kein_neues_ziel() -> None:
    state = evaluate(_nights([58, 57, 59, 56, 58, 57, 58, 57]), {"w": 118, "date": "x"}, LAST)
    assert state["level"] == "very_good"
    assert state["done"] is True
    assert state["goal_w"] is None
    wins = new_wins(state, {"w": 118, "date": "x"}, {})
    assert {"very_good", "held_4", "minus_10"} <= set(wins)


def test_ziel_nie_unter_dauerverbrauch() -> None:
    state = evaluate(_nights([64] * 8), {"w": 64, "date": "x"}, LAST)
    assert state["goal_w"] >= FLOOR_W


def test_anstieg_freundlich_und_nach_vier_wochen_normal() -> None:
    state = evaluate(_nights([58, 57, 59, 57, 58, 57, 58, 83]), {"w": 118, "date": "x"}, LAST)
    assert state["rise"] == {"from_w": 58, "by_w": 26}
    assert state["goal_w"] == 60
    # Vier Wochen später ist der neue Wert normal: kein Hinweis mehr.
    later = evaluate(_nights([58, 57, 58, 83, 84, 83, 84, 83]), {"w": 118, "date": "x"}, LAST)
    assert later["rise"] is None


def test_erfolge_bleiben() -> None:
    state = evaluate(_nights([80] * 8), {"w": 142, "date": "x"}, LAST)
    assert set(new_wins(state, {"w": 142, "date": "x"}, {})) == {"minus_10", "good"}
    # Einmal erreicht, wird nichts doppelt vergeben – und nichts genommen.
    assert new_wins(state, {"w": 142, "date": "x"}, {"minus_10": "2026-10-01", "good": "2026-10-08"}) == {}


def test_urlaub_zaehlt_nicht() -> None:
    nights = _nights([90] * 8)
    for d in range(7):  # letzte Woche verreist
        nights[(LAST - timedelta(days=d)).isoformat()] = None
    state = evaluate(nights, {"w": 90, "date": "x"}, LAST)
    assert state["current_w"] is None


async def test_ausgangswert_und_websocket(hass: HomeAssistant, entry, hass_ws_client) -> None:
    from homeassistant.setup import async_setup_component  # noqa: PLC0415

    from .test_ablauf import _setup  # noqa: PLC0415

    assert await async_setup_component(hass, "websocket_api", {})
    bewohner = await _setup(hass, entry)
    hass.config_entries.async_update_entry(entry, options={**entry.options, CONF_GRID_ENERGY: "sensor.zaehler"})
    gv: Grundverbrauch = bewohner.grundverbrauch
    last = gv._last_night()  # noqa: SLF001
    fake = {(last - timedelta(days=d)).isoformat(): 120.0 for d in range(20)}

    async def _measure(self, days, statistic_id, person):
        return {d.isoformat(): fake[d.isoformat()] for d in days if d.isoformat() in fake}

    with patch.object(Grundverbrauch, "_measure", _measure):
        gv.data["nights"] = {k: v for k, v in fake.items() if k < (last - timedelta(days=9)).isoformat()}
        await gv.async_update()
    assert gv.data["start"]["w"] == 120

    ws = await hass_ws_client(hass)
    await ws.send_json_auto_id({"type": "werner/baseload", "entry_id": entry.entry_id})
    res = await ws.receive_json()
    assert res["success"], res
    model = res["result"]
    assert model["configured"] is True
    assert model["current_w"] == 120
    assert model["level"] == "medium"
    assert model["price_assumed"] is True
