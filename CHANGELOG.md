# Änderungen

## 1.1.1 – 2026-11-26

- Farben von „Mein Zuhause“ und Logo nach dem Erscheinungsbild von effizientes-heim.de: Violett #381D92 für Knöpfe und Auswahl, Lavendel #F2F2FA als Grund, Tinte #0B0620 für Text. Grün und Rot für „in Ordnung“ und „Hilfe“ bleiben.

## 1.1.0 – 2026-11-26

- **Grundverbrauch statt Zählerstand.** „Mein Zuhause“ › Energie zeigt, was rund um die Uhr läuft – gemessen nachts zwischen 1 und 5 Uhr, nur in Nächten, in denen der Bewohner zu Hause ist (Urlaub zählt nicht).
- **Anerkennen statt antreiben:** Werner zeigt, wie viel seit dem Ausgangswert eingespart ist (Watt und Euro im Jahr), und vergibt Erfolge, die bleiben – etwa „Erstmals 10 Watt weniger“ oder „Stufe sehr gut erreicht“.
- Stufen für einen 1-Personen-Haushalt: sehr gut bis 60 W, gut bis 100 W, mittel bis 150 W. Werner schlägt nur kleine Schritte vor (etwa 10 Prozent). Ab „sehr gut“ gibt es kein neues Ziel mehr, nur „Halten genügt“; unter das, was dauernd laufen muss, setzt Werner nie ein Ziel.
- Steigt der Grundverbrauch merklich, gibt es einen freundlichen Hinweis. Bleibt er vier Wochen oben, gilt er als neuer Normalfall.
- Euro-Beträge mit dem mittleren Nord-Pool-Preis, sonst mit 30 ct je kWh.
- Eine von Werner angelegte „Solaranlage (Werner)“ wird nach einer Neueinrichtung wieder als eigene Anlage erkannt.

## 1.0.0 – 2026-11-25

- **Werner ist eine Option.** „Mein Zuhause“ startet mit Energie und Einstellungen. Das Warnsystem Werner ist bei neuen Einrichtungen ausgeschaltet; der Bewohner schaltet es unter „Einstellen“ bewusst ein („Werner einschalten“, mit Erklärung in einfacher Sprache) und kann es dort jederzeit wieder ausschalten. Die Einstellungen bleiben dabei erhalten.
- Ist Werner aus, zeigt „Mein Zuhause“ nur die Reiter Einstellen, (Auto) und Energie – Energie steht an erster Stelle. Die Reiter Start und Werner erscheinen erst, wenn Werner eingeschaltet ist.
- Neuer Schalter „Werner eingeschaltet“ und Status „Ausgeschaltet“. Bestehende Einrichtungen bleiben eingeschaltet.
- **Eigenes Logo:** Werner als freundliches Haus mit Gesicht. Home Assistant zeigt es bei Installation, Update, unter „Geräte & Dienste“ und im Marketplace – in hellem und dunklem Design (Ordner `brand/`, ab Home Assistant 2026.3).

## 0.9.0 – 2026-11-25

- **Solaranlage selbst einrichten:** Unter Energie › „Was hier angezeigt wird – ändern“ fragt Werner in einfachen Worten nach Leistung in Watt, Himmelsrichtung („nach Süden“) und Aufstellung („senkrecht – am Balkongeländer“, „schräg wie ein Hausdach“ …). Werner legt dafür selbst einen Eintrag der eingebauten Integration Forecast.Solar am Standort des Zuhauses an; Ändern und Entfernen betrifft nur diesen eigenen Eintrag. Ein Helfer ist dafür nicht mehr nötig.

## 0.8.0 – 2026-11-25

- **Diagramme „Strom heute und morgen“** im Bildschirm Energie, groß und in einfacher Sprache, mit Markierung „jetzt“:
  - **Strompreis** je Stunde von 6 Stunden zurück bis 24 Stunden voraus (grün günstig, rot teuer) mit Satz „Am günstigsten: …“ – aus der eingebauten Integration Nord Pool, wahlweise mit Mehrwertsteuer und festem Aufschlag.
  - **Sonnenstrom-Vorhersage** für heute und morgen aus der eingebauten Integration Forecast.Solar.
  - **Stromverbrauch der Wohnung**: die letzten 12 Stunden aus der Statistik, dazu die Erwartung für die nächsten 6 Stunden (Durchschnitt derselben Uhrzeit an den letzten bis zu 14 Tagen).
- „Was hier angezeigt wird – ändern“: Quelle für Strompreis und Sonnen-Vorhersage, Mehrwertsteuer und Aufschlag.

## 0.7.1 – 2026-11-24

- **Verständliche Nachrichten an Vertrauenspersonen.** Jede Nachricht (App, Signal, E-Mail) sagt jetzt: was los ist, warum gerade diese Person sie bekommt, was sie tun soll und was jede Antwort bewirkt (1 = Ich kümmere mich, 2 = Fehlalarm, 3 = Ich kann gerade nicht – mit Namen der nächsten Person).
- Der Grund wird für Vertrauenspersonen in der dritten Person geschrieben („bei Erika“ statt „bei Ihnen“) und nennt Uhrzeit und Wartezeit der Nachfrage.
- Test-Nachrichten erklären, wie ein echter Alarm abläuft.
- „Werner einstellen“: Kurztexte je Weg erklären die Antworten; ein ausklappbares Beispiel zeigt, wie eine Nachricht an die Person aussieht.

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
