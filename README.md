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

Für jeden Bewohner einmal hinzufügen.

Die Knöpfe öffnen Ihr eigenes Home Assistant über my.home-assistant.io. Beim ersten Mal fragt die Seite nach der Adresse Ihres Home Assistant. Werner und alle Daten bleiben bei Ihnen zu Hause.

## Stand der Entwicklung

Werner gibt es heute in zwei Formen:

- **YAML-Paket (heute nutzbar):** Helfer, Skripte und Automationen zum Kopieren, mit der Karte „Mein Zuhause“. Für einen Bewohner, Einrichtung von Hand. Anleitung: [Werner als YAML-Paket](docs/einrichtung/README.md).
- **Integration (Ziel, im Aufbau):** Installation über HACS mit den Knöpfen oben, Einrichtung per Assistent, mehrere Bewohner. Sie übernimmt Schritt für Schritt alles aus dem Paket und ersetzt es dann.

| Teil | YAML-Paket | Integration |
|---|---|---|
| Installation | Dateien kopieren | über HACS |
| Bewohner anlegen | von Hand | Einrichtungs-Assistent |
| Nachfragen und Vertrauenspersonen informieren | vorhanden | vorhanden, neustartfest |
| Wege: HA-App, Signal, E-Mail | vorhanden | HA-App vorhanden, Signal und E-Mail in Arbeit |
| Dashboard „Mein Zuhause“ | Karte von Hand einbinden | geplant: wird automatisch angelegt |
| Mehrere Bewohner | nein | vorgesehen: ein Eintrag je Bewohner |
| Kamera und Mikrofon (nur mit Zustimmung) | nein | geplant |
| Aufnahme in die HACS-Standardliste | – | geplant |

## Inhalt des Repositorys

| Ordner | Inhalt |
|---|---|
| `custom_components/werner/` | Integration (Ziel) |
| `packages/werner.yaml` | YAML-Paket (Übergang) |
| `card/` | Karte `mein-zuhause-card` |
| `scripts/werner_mail.py` | E-Mail-Versand für das YAML-Paket |
| `themes/` | Theme `mein_zuhause` |
| `examples/` | Beispiel-Dashboard mit Musterdaten |
| `blueprints/` | geplant: weitere Aktivitätsquellen |
| `docs/` | Anleitungen |

## Grundsätze

- **Selbstbestimmt:** Der Bewohner legt fest, wer wie und wann informiert wird. Er kann Werner jederzeit pausieren.
- **Erst fragen, dann melden:** Werner fragt immer zuerst den Bewohner.
- **Kostenlos:** Benachrichtigung über die Home-Assistant-App, Signal oder E-Mail. Angehörige brauchen keine zusätzliche App. [Warum nicht WhatsApp oder Threema?](docs/einrichtung/installation.md#warum-nicht-whatsapp-oder-threema)
- **Daten bleiben im Haus:** Verarbeitung nur lokal. Vertrauenspersonen bekommen nur die Meldung und die Uhrzeit – nie Bilder, Töne oder den Tagesablauf. Mehr dazu: [Datenschutz](docs/datenschutz.md).
- **Einfache Sprache** für alles, was der Bewohner sieht.

## Anleitungen

- [So funktioniert Werner – in einfacher Sprache](docs/einfach/so-funktioniert-werner.md)
- [Installation und Einrichtung – für Helfer](docs/einrichtung/installation.md)
- [Werner als YAML-Paket – Übergangslösung](docs/einrichtung/README.md)
- [Energie (optional)](docs/energie/README.md)
- [Datenschutz](docs/datenschutz.md)

## Abhängigkeiten (nicht enthalten)

Diese Bausteine werden nur verlinkt, nicht mitgeliefert. Es gelten ihre eigenen Lizenzen:

- [Home Assistant](https://www.home-assistant.io/)
- [HACS](https://hacs.xyz/)
- App „Signal Messenger“ für Home Assistant ([haberda/hassio_addons](https://github.com/haberda/hassio_addons)) auf Basis von [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api)
- [navbar-card](https://github.com/joseluis9595/lovelace-navbar-card)
- optional [evcc](https://evcc.io/)

## Mitmachen

Fragen, Fehler und Ideen bitte als [Issue](https://github.com/consulting-kleimanns/werner-home-assistant/issues). Regeln fürs Mitmachen: [CONTRIBUTING](CONTRIBUTING.md). Änderungen stehen im [Changelog](CHANGELOG.md).

## Lizenz

[MIT](LICENSE)
