# Änderungen

## 0.7.0 – 2026-11-24
- **E-Mail** als Weg zu den Vertrauenspersonen. Ein Helfer trägt einmal ein eigenes Postfach für Werner ein (Einstellen › Wer & wie, nur für Administratoren, mit Vorlagen für GMX, WEB.DE, Gmail, T-Online, Outlook und Test-E-Mail). Das Passwort liegt im Speicher von Home Assistant, nicht in einer Entität.
- Antwort **per Klick in der E-Mail** (Ich kümmere mich, Fehlalarm, Kann nicht), wenn Home Assistant von außen erreichbar ist. Erst der Knopf auf der geöffneten Seite zählt, damit Virenscanner nichts auslösen. Die Links gelten nur für diesen einen Alarm.
- Karte einstellbar: `screen`, `hide_tabs`, `resident`.
- **Aufgeräumt:** YAML-Paket, alte Karte `mein-zuhause-card`, Beispiel-Dashboard, Theme und Mail-Skript entfernt – die Integration kann alles davon. Letzter Stand mit Paket: Commit `db2d168`.

## 0.6.0 – unveröffentlicht
Einrichtung flüssiger und seniorengerecht.
- **Einrichtungs-Assistent:** Nur noch die Person wählen. Den Namen (Vorname) und das Handy (HA-App, mit der sich die Person anmeldet) findet Werner selbst. Gibt es noch keine Person, sagt der Assistent, was zu tun ist.
- **„So weit ist Werner eingerichtet“:** Unter Einstellen zeigt eine Liste, was noch fehlt (Handy, Vertrauensperson, Aktivitätsquellen, Signal). Jeder offene Punkt führt direkt an die richtige Stelle. Auf dem Startbildschirm erinnert ein Hinweis, solange etwas fehlt.
- **Signal mit zwei Geräten:** Am Handy kann man den eigenen Code nicht scannen. Werner bietet deshalb „Code auf anderem Gerät zeigen“ an: einen Link (kopieren oder schicken), der auf Computer oder Tablet direkt den Code öffnet. Werner merkt von selbst, wenn die Verbindung geklappt hat.
- **Geräte-Auswahl mit aktuellem Wert:** Aktivitätsquellen und Energie-Anzeige zeigen zu jedem Gerät Raum und Wert von gerade eben (z. B. „291 W“, „Bewegung erkannt“, „zu“). Technische Namen werden lesbar gemacht.
- Eigenes Handy wird beim Einschalten von Werner vorgeschlagen; beim Eintragen weiterer Bewohner nimmt Werner automatisch deren Handy.
- Anleitung für Helfer überarbeitet; Hinweis, den Port der Signal-App nicht freizugeben.

## 0.5.0 – unveröffentlicht
- **Signal** als Weg zu den Vertrauenspersonen: Werner schreibt über die App „Signal Messenger“, die Person antwortet mit 1, 2 oder 3. Werner findet die App selbst. Verbinden per QR-Code in „Mein Zuhause“.
- **Energie-Anzeige** wählt der Bewohner selbst (Wetter, Netz, Zählerstand, Sonne, Batterie, Auto).

## 0.4.0 – unveröffentlicht
- **Selbstbestimmung:** Bewohner schalten Werner in „Mein Zuhause“ selbst ein und tragen weitere Bewohner ein. Diese müssen mit ihrer eigenen Anmeldung zustimmen; lehnen sie ab, wird der Eintrag gelöscht. Jeder sieht nur seine eigenen Einstellungen und sein Protokoll.
- **Aktivitätsquellen** wählt der Bewohner selbst (Stromverbrauch, Bewegung und Türen, Fernseher und Musik), dazu die Grundlast.

## 0.3.0 – unveröffentlicht
- Oberfläche **„Mein Zuhause“** kommt mit der Integration: als Bereich in der Seitenleiste (`/werner`) und als Karte `custom:werner-mein-zuhause`. Bildschirme Start, Werner, Energie, Auto, Einstellen.

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
