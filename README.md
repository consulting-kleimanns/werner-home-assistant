<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="custom_components/werner/brand/dark_logo.png"><img src="custom_components/werner/brand/logo.png" alt="Werner" width="330"></picture></p>

# Werner – ein freundlicher Aufpasser für Senioren

**Werner** ist ein Warnsystem für Home Assistant. Es merkt, wenn es bei einem allein lebenden Menschen ungewöhnlich still ist – oder nachts ungewöhnlich viel passiert. Dann fragt Werner **zuerst den Bewohner selbst**: „Ist alles in Ordnung?“ Erst wenn keine Antwort kommt, informiert Werner nacheinander die Vertrauenspersonen, die der Bewohner selbst ausgewählt hat.

Dazu gehört **Mein Zuhause**: ein Dashboard in einfacher Sprache, mit großen Knöpfen, ohne Fachbegriffe. Optional zeigt es auch Energie (Stromzähler, Balkonkraftwerk, Wallbox über evcc) und gibt Tipps nach der Wettervorhersage.

> **Werner ist kein Hausnotruf und kein Medizinprodukt.** Er ersetzt keinen Notruf. **Im Notfall: 112.**

## Installieren

Sie brauchen [Home Assistant](https://www.home-assistant.io/installation/) und [HACS](https://hacs.xyz/). Fehlt etwas? Die [Anleitung für Helfer](docs/einrichtung/installation.md) erklärt alles Schritt für Schritt.

**1. Werner herunterladen**

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=consulting-kleimanns&repository=werner-home-assistant&category=integration)

In HACS auf **Herunterladen** tippen und Home Assistant neu starten.

**2. Werner hinzufügen und einrichten**

[![Werner hinzufügen](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=werner)

Der Assistent fragt nur, für wen Werner da sein soll. Danach steht **„Mein Zuhause“** in der Seitenleiste. Dort richtet der Bewohner alles Weitere selbst ein – eine Liste zeigt, was noch fehlt. Weitere Bewohner schalten Werner dort für sich selbst ein.

Die Knöpfe öffnen Ihr eigenes Home Assistant über my.home-assistant.io. Beim ersten Mal fragt die Seite nach der Adresse Ihres Home Assistant. Werner und alle Daten bleiben bei Ihnen zu Hause.

## Als Karte in eigenen Dashboards

„Mein Zuhause“ gibt es auch als Karte, z. B. für ein Tablet an der Wand:

```yaml
type: custom:werner-mein-zuhause
screen: werner          # Start-Bildschirm: start, werner, energie, auto, einstellen
hide_tabs: true         # Reiterleiste ausblenden (optional)
resident: person.erika  # nur für Helfer: diesen Bewohner zeigen (optional)
```

Jeder Bewohner sieht immer nur sich selbst; `resident` gilt nur für Administratoren.

## Stand der Entwicklung

| Teil | Stand |
|---|---|
| Installation | über HACS, Assistent fragt nur nach der Person |
| Nachfragen und Vertrauenspersonen informieren | vorhanden, neustartfest |
| Wege: HA-App, Signal, E-Mail | alle drei, mit Antwort 1/2/3 (bei E-Mail per Klick) |
| Oberfläche „Mein Zuhause“ | kommt mit, in der Seitenleiste und als Karte |
| Einstellungen durch den Bewohner selbst | ja, inklusive Aktivitätsquellen und Energie-Anzeige |
| Mehrere Bewohner | ja, jeder mit eigener Zustimmung |
| Kamera und Mikrofon (nur mit Zustimmung) | Zustimmung vorhanden, Auswertung geplant |
| Aufnahme in die HACS-Standardliste | geplant |

Offene Punkte stehen als [Issues](https://github.com/consulting-kleimanns/werner-home-assistant/issues). Das frühere YAML-Paket ist entfernt; die Integration kann alles, was es konnte. Der letzte Stand mit Paket liegt in Commit [`db2d168`](https://github.com/consulting-kleimanns/werner-home-assistant/tree/db2d168).

## Inhalt des Repositorys

| Ordner | Inhalt |
|---|---|
| `custom_components/werner/` | Integration mit Oberfläche „Mein Zuhause“ |
| `docs/` | Anleitungen |
| `tests/` | automatische Tests |

## Grundsätze

- **Selbstbestimmt:** Der Bewohner legt fest, wer wie und wann informiert wird. Er kann Werner jederzeit pausieren.
- **Erst fragen, dann melden:** Werner fragt immer zuerst den Bewohner.
- **Kostenlos:** Benachrichtigung über die Home-Assistant-App, Signal oder E-Mail. Angehörige brauchen keine zusätzliche App. [Warum nicht WhatsApp oder Threema?](docs/einrichtung/installation.md#warum-nicht-whatsapp-oder-threema)
- **Daten bleiben im Haus:** Verarbeitung nur lokal. Vertrauenspersonen bekommen nur die Meldung und die Uhrzeit – nie Bilder, Töne oder den Tagesablauf. Mehr dazu: [Datenschutz](docs/datenschutz.md).
- **Einfache Sprache** für alles, was der Bewohner sieht.

## Anleitungen

- [So funktioniert Werner – in einfacher Sprache](docs/einfach/so-funktioniert-werner.md)
- [Installation und Einrichtung – für Helfer](docs/einrichtung/installation.md)
- [Energie (optional)](docs/energie/README.md)
- [Datenschutz](docs/datenschutz.md)

## Abhängigkeiten (nicht enthalten)

Diese Bausteine werden nur verlinkt, nicht mitgeliefert. Es gelten ihre eigenen Lizenzen:

- [Home Assistant](https://www.home-assistant.io/)
- [HACS](https://hacs.xyz/)
- App „Signal Messenger“ für Home Assistant ([haberda/hassio_addons](https://github.com/haberda/hassio_addons)) auf Basis von [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api)
- optional [evcc](https://evcc.io/)

## Mitmachen

Fragen, Fehler und Ideen bitte als [Issue](https://github.com/consulting-kleimanns/werner-home-assistant/issues). Regeln fürs Mitmachen: [CONTRIBUTING](CONTRIBUTING.md). Änderungen stehen im [Changelog](CHANGELOG.md).

## Lizenz

[MIT](LICENSE)
