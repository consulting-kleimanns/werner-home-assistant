# Änderungen

## 0.2.0 – unveröffentlicht
Erster Schritt zur Werner-Integration, die das YAML-Paket später ersetzt.
- Installation über HACS (als benutzerdefiniertes Repository) mit den Knöpfen „In HACS öffnen“ und „Werner hinzufügen“ im README.
- Integration `werner`: Einrichtungs-Assistent legt je Bewohner einen Eintrag an (Name, Person, Handy).
- Warnlogik in der Integration: je Bewohner ein Gerät mit Status, letzter Aktivität, Pause, Regeln, Wartezeit, drei Vertrauenspersonen und den Knöpfen „Alles gut“ und „Ich brauche Hilfe“. Werner fragt zuerst den Bewohner und informiert dann die Vertrauenspersonen nacheinander per Home-Assistant-App (Antwort 1/2/3). Ein laufender Ablauf geht nach einem Neustart weiter. Signal und E-Mail folgen.
- Optionen je Bewohner: Aktivitätsquellen und Grundlast in Watt.
- Tests mit pytest-homeassistant-custom-component.
- Anleitungen: Installation für Helfer (inkl. „Warum nicht WhatsApp oder Threema?“), Datenschutz.
- Automatische Prüfung mit hassfest.

## 0.1.0 – 2026-11-23
Erste öffentliche Fassung aus einer laufenden Installation, anonymisiert und verallgemeinert.
- Package `werner.yaml`: Helfer, Nachfrage, Eskalation an bis zu 3 Vertrauenspersonen (HA-App mit Antwortknöpfen, Signal, E-Mail), Pause, Regeln.
- Karte `mein-zuhause-card` 0.1.0: Bildschirme Start, Werner, Energie, Auto, Einstellen; Signal-Verbindung per QR-Code; Einzeltest je Vertrauensperson; SMTP-Einstellungen; Erklärung in einfacher Sprache.
- `werner_mail.py` für frei einstellbaren SMTP-Versand.
- Theme `mein_zuhause`, Beispiel-Dashboard, Anleitungen.

## Anfang
- Repository angelegt: README, MIT-Lizenz, geplanter Aufbau.
