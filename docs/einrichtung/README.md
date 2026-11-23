# Einrichtung für Helfer

> Das ist die heute nutzbare Fassung als YAML-Paket. Ziel ist die Integration mit Installation über HACS, siehe [Installation und Einrichtung](installation.md). Sie ersetzt das Paket, sobald sie alle Funktionen hat.

Diese Anleitung richtet Werner und das Dashboard „Mein Zuhause“ in einem bestehenden Home Assistant ein (getestet mit HA OS 2026.11).

## 1. Voraussetzungen
- Home Assistant mit der **HA-App** auf dem Handy des Bewohners (für Nachfrage und Anwesenheit).
- Optional **Signal**: HA-App-Repository `https://github.com/haberda/hassio_addons` hinzufügen, App „Signal Messenger“ installieren, Modus **json-rpc** wählen, starten.
- Optional **E-Mail**: ein eigenes Postfach nur für Werner (z. B. bei GMX mit freigeschaltetem SMTP).
- Frontend: [navbar-card](https://github.com/joseluis9595/lovelace-navbar-card) als Dashboard-Ressource.

## 2. Dateien kopieren
| Repo | Ziel in Home Assistant |
|---|---|
| `packages/werner.yaml` | `/config/packages/werner.yaml` |
| `scripts/werner_mail.py` | `/config/werner/werner_mail.py` |
| `themes/mein_zuhause.yaml` | `/config/themes/mein_zuhause.yaml` |
| `card/mein-zuhause-card.js` | `/config/www/mein-zuhause/mein-zuhause-card.js` |

In `configuration.yaml`:
```yaml
homeassistant:
  packages: !include_dir_named packages
frontend:
  themes: !include_dir_merge_named themes
```

## 3. Package anpassen
Am Anfang von `werner.yaml` stehen Platzhalter (`person.bewohner`, `notify.mobile_app_bewohner_handy`, …). Durch die echten Entity-IDs ersetzen, dann **Konfiguration prüfen** und HA neu starten.

## 4. Dashboard
1. Ressourcen anlegen (Einstellungen → Dashboards → Ressourcen):
   - `/local/mein-zuhause/mein-zuhause-card.js` – JavaScript-Modul
   - navbar-card – JavaScript-Modul
   - `https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap` – Stylesheet
2. Neues Dashboard mit URL-Pfad `mein-zuhause` anlegen, Rohkonfiguration öffnen, `examples/dashboard-mein-zuhause.yaml` einfügen und die Musterdaten ersetzen.
3. Dashboard als Standard für den Bewohner setzen, Theme `mein_zuhause` wählen.
4. Die HA-Kopfzeile wird auf diesem Dashboard ausgeblendet. Zum Bearbeiten `?kopf=1` an die Adresse hängen.

## 5. Einstellen (zusammen mit dem Bewohner)
Im Dashboard unter **Einstellen**:
- **Wer & wie:** Vertrauenspersonen eintragen, Weg wählen (HA-App, Signal, E-Mail). **Jede Person einzeln testen** („Test-Nachricht an diese Person senden“).
- **Signal verbinden:** QR-Code auf einem zweiten Gerät (z. B. Tablet) anzeigen und mit dem Handy des Bewohners in Signal → Einstellungen → Verknüpfte Geräte scannen.
- **Wann:** Regeln und Wartezeit einstellen.
- **E-Mail:** Anbieter wählen, Benutzer und Passwort eintragen, Test-E-Mail senden. Das Passwort liegt als Helfer in HA – deshalb ein Postfach nur für Werner nehmen.

## 6. Regeln aktivieren
`automation.werner_regeln_prufen` ist zunächst aus. Erst einschalten, wenn eine verlässliche Aktivitätsquelle angebunden ist (z. B. Hausstromverbrauch) – sonst gibt es Fehlalarme. Danach einen Ende-zu-Ende-Test mit allen Beteiligten absprechen.

## Bekannte Grenzen (Version 0.1)
- Ein Bewohner pro Installation (mehrere Bewohner sind geplant).
- Antworten per Signal (1/2/3) werden noch nicht ausgewertet; Werner wartet 15 Minuten und geht dann zur nächsten Person.
- SMS ist vorgesehen, aber nicht umgesetzt.
