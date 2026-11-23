# Werner – ein freundlicher Aufpasser für Senioren

**Werner** ist ein Warnsystem für Home Assistant. Es merkt, wenn es bei einem allein lebenden Menschen ungewöhnlich still ist – oder nachts ungewöhnlich viel passiert. Dann fragt Werner **zuerst die Person selbst**: „Ist alles in Ordnung?“ Erst wenn keine Antwort kommt, informiert Werner nacheinander die Vertrauenspersonen, die der Bewohner selbst ausgewählt hat.

Dazu gehört **Mein Zuhause**: ein Dashboard in einfacher Sprache, mit großen Knöpfen, ohne Fachbegriffe. Optional zeigt es auch Energie (Stromzähler, Balkonkraftwerk, Wallbox über evcc) und gibt Tipps nach der Wettervorhersage.

> **Status:** im Aufbau. Werner läuft bereits in einer ersten echten Installation. Die allgemeine, konfigurierbare Fassung entsteht hier Schritt für Schritt.

## Grundsätze

- **Selbstbestimmt:** Der Bewohner legt fest, wer wie und wann informiert wird. Er kann Werner jederzeit pausieren.
- **Erst fragen, dann melden:** Werner fragt immer zuerst den Bewohner.
- **Kostenlos:** Benachrichtigung über die Home-Assistant-App, Signal oder E-Mail. Angehörige brauchen keine zusätzliche App.
- **Daten bleiben im Haus:** Verarbeitung nur lokal. Vertrauenspersonen bekommen nur die Meldung und die Uhrzeit – nie Bilder, Töne oder den Tagesablauf.
- **Einfache Sprache** für alles, was der Bewohner sieht.

## Wichtig

Werner ist **kein Hausnotruf und kein Medizinprodukt**. Er ersetzt keinen Notruf. **Im Notfall: 112.**

## Geplanter Aufbau

| Ordner | Inhalt |
|---|---|
| `card/` | Lovelace-Karte `mein-zuhause-card` (HACS-fähig, konfigurierbar) |
| `packages/` | Home-Assistant-Package `werner.yaml`: Helfer, Skripte, Automationen |
| `scripts/` | `werner_mail.py` – E-Mail-Versand über frei einstellbaren SMTP-Dienst |
| `blueprints/` | Bausteine für Aktivitätsquellen und Nachfrage-Regeln |
| `themes/` | Theme `mein_zuhause` (hell, gut lesbar) |
| `docs/einfach/` | Anleitung für Senioren in einfacher Sprache |
| `docs/einrichtung/` | Schritt-für-Schritt-Anleitung für Helfer |
| `docs/energie/` | Optionaler Energie-Teil (evcc, Zähler, Balkonkraftwerk, Wallbox) |
| `examples/` | Beispiel-Dashboard mit Musterdaten |

## Abhängigkeiten (nicht enthalten)

Diese Bausteine werden nur verlinkt, nicht mitgeliefert. Es gelten ihre eigenen Lizenzen:

- [Home Assistant](https://www.home-assistant.io/)
- [navbar-card](https://github.com/joseluis9595/lovelace-navbar-card)
- [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) bzw. die Home-Assistant-App „Signal Messenger“
- optional [evcc](https://evcc.io/)

## Lizenz

[MIT](LICENSE)
