# Werner installieren und einrichten – für Helfer

Diese Anleitung ist für die Person, die Werner beim Bewohner einrichtet: Angehörige, Nachbarn oder ein Techniker. Für den Bewohner selbst gibt es die Erklärung [So funktioniert Werner](../einfach/so-funktioniert-werner.md).

Richten Sie Werner **gemeinsam mit dem Bewohner** ein. Was der Bewohner selbst entscheidet – wer informiert wird, wann Werner nachfragt, Kamera und Mikrofon – stellt er in seinem Dashboard ein.

> Werner ist kein Hausnotruf und kein Medizinprodukt. Im Notfall gilt immer 112.

> **Übergang:** Die Integration ist noch im Aufbau. Wer Werner heute schon nutzen will, nimmt das [YAML-Paket](README.md). Die Schritte 1, 2 und 5 gelten für beide Wege.

## Überblick

| Schritt | Was | Wie oft |
|---|---|---|
| 1 | Home Assistant bereitstellen | einmal |
| 2 | Konto und Handy für jeden Bewohner | je Bewohner |
| 3 | HACS einrichten | einmal |
| 4 | Werner herunterladen | einmal |
| 5 | Signal vorbereiten (empfohlen) | einmal |
| 6 | Werner hinzufügen und einrichten | je Bewohner |
| 7 | Testen, Updates, Sicherung | regelmäßig |

## 1. Home Assistant bereitstellen

**Schon vorhanden?** Sie brauchen ein Konto mit Administrator-Rechten und eine aktuelle Version (Einstellungen › Updates).

**Neu einrichten:**

1. Gerät besorgen, z. B. Home Assistant Green oder einen Raspberry Pi mit Home Assistant OS.
2. Mit einem Netzwerkkabel an den Router anschließen und einschalten.
3. Im Browser `http://homeassistant.local:8123` öffnen.
4. Ihr eigenes Helfer-Konto anlegen (Administrator) und den Standort des Hauses eintragen.

Ausführlich: [home-assistant.io/installation](https://www.home-assistant.io/installation/)

## 2. Konto und Handy für jeden Bewohner

Jeder Bewohner bekommt ein **eigenes Konto**. So fragt Werner immer die richtige Person, und jeder sieht nur seine eigenen Einstellungen.

1. Einstellungen › Personen › **Person hinzufügen**
2. Name eintragen, **Darf sich anmelden** einschalten, **Administrator** ausgeschaltet lassen.

Auf dem Handy des Bewohners:

- [ ] Home-Assistant-App installieren und mit dem Konto des Bewohners anmelden
- [ ] Mitteilungen erlauben – auf dem iPhone auch „Zeitkritisch“
- [ ] Standort auf „Immer“ stellen
- [ ] Optional: „Bewegung & Fitness“ freigeben (Schritte)

Für jeden weiteren Bewohner wiederholen.

## 3. HACS einrichten

HACS ist der Laden für Erweiterungen von Home Assistant. Werner kommt von dort – auch alle Updates.

1. Der Anleitung auf [hacs.xyz](https://hacs.xyz/) folgen.
2. Home Assistant neu starten.
3. Einstellungen › Geräte & Dienste › Integration hinzufügen › **HACS**
4. Mit einem kostenlosen GitHub-Konto bestätigen.

## 4. Werner herunterladen

Am schnellsten über den Knopf:

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=consulting-kleimanns&repository=werner-home-assistant&category=integration)

1. Beim ersten Mal fragt my.home-assistant.io nach der Adresse Ihres Home Assistant, z. B. `http://homeassistant.local:8123`.
2. HACS öffnet Werner. Auf **Herunterladen** tippen.
3. Home Assistant neu starten.

**Von Hand:** Solange Werner nicht in der HACS-Standardliste steht, in HACS oben rechts ⋮ › Benutzerdefinierte Repositories › `https://github.com/consulting-kleimanns/werner-home-assistant`, Typ **Integration**. Danach Werner suchen und herunterladen.

## 5. Signal vorbereiten (empfohlen)

Über Signal erreicht Werner die Vertrauenspersonen kostenlos und ohne zusätzliche App für sie. Dafür braucht Home Assistant die App „Signal Messenger“.

1. Einstellungen › Apps › App-Store › ⋮ › Repositories › `https://github.com/haberda/hassio_addons` hinzufügen.
2. **Signal Messenger** installieren.
3. Unter Konfiguration den Modus **json-rpc** wählen und die App starten.

Im Modus `normal` dauert das Erzeugen des QR-Codes sehr lange. Verbunden wird später mit dem Signal-Konto des Bewohners: Der Bewohner zeigt den QR-Code im Dashboard auf dem Tablet und scannt ihn mit seinem Handy (Signal › Einstellungen › Verknüpfte Geräte).

## 6. Werner hinzufügen und einrichten

[![Werner hinzufügen](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=werner)

Oder von Hand: Einstellungen › Geräte & Dienste › Integration hinzufügen › **Werner**.

Der Assistent fragt je Bewohner:

| Feld | Beispiel |
|---|---|
| Name (so spricht Werner ihn an) | Erika |
| Person in Home Assistant | `person.erika` |
| Benachrichtigungsdienst des Handys | `mobile_app_erikas_handy` |

Für jeden weiteren Bewohner Werner noch einmal hinzufügen.

Danach gibt es für den Bewohner ein Gerät **„Werner · Erika“** (Einstellungen › Geräte & Dienste › Werner) mit allen Einstellungen und Knöpfen.

### Aktivitätsquellen einstellen

Einstellungen › Geräte & Dienste › Werner › beim Bewohner **Konfigurieren**:

- **Aktivitätsquellen:** z. B. der Leistungssensor des Stromzählers, Bewegungsmelder, das Tablet. Jede Änderung zählt als Aktivität.
- **Grundlast:** Strom, der immer läuft (Kühlschrank, Standby), z. B. 300 W. Bei Zahlen zählt nur ein Anstieg über die Grundlast.

Die Regeln „Morgens nichts los“ und „Tagsüber lange still“ arbeiten erst, wenn mindestens eine Quelle gewählt ist – sonst gäbe es Fehlalarme.

### Vertrauenspersonen eintragen

Am Gerät des Bewohners für Person 1 bis 3: **Name**, **Weg** und beim Weg Home-Assistant-App das **App-Gerät** (z. B. `mobile_app_sabines_handy`). Die Vertrauensperson braucht dafür die Home-Assistant-App mit einem eigenen Konto in diesem Home Assistant.

> **In Arbeit:** Die Wege Signal und E-Mail in der Integration, weitere Schritte des Assistenten und das automatisch angelegte Dashboard „Mein Zuhause“. Bis dahin überspringt Werner Personen mit Signal oder E-Mail und schreibt das ins Protokoll.

### Woran Werner Aktivität erkennt

Jede Quelle gehört entweder zu einem Bewohner oder zum ganzen **Haushalt**:

| Quelle | Gehört meist zu |
|---|---|
| Stromzähler (Wasserkocher, Herd, Fernseher) | Haushalt |
| Handy des Bewohners | dem Bewohner |
| Tablet | dem Bewohner, der es nutzt |
| Bewegungsmelder | Haushalt |

Aktivität im Haushalt beruhigt Werner nie für einen einzelnen Bewohner: Ist nur einer aktiv, fragt Werner beim anderen trotzdem nach.

**Kamera und Mikrofon** schalten Sie als Helfer nicht ein. Das entscheidet jeder Bewohner selbst in seinem Dashboard. Siehe [Datenschutz](../datenschutz.md).

### Wege zu den Vertrauenspersonen

| Weg | Kosten | Antwort möglich |
|---|---|---|
| Home-Assistant-App | kostenlos | ja: 1 kümmere mich, 2 Fehlalarm, 3 nächste Person |
| Signal | kostenlos | ja |
| E-Mail | kostenlos (eigenes Postfach für Werner) | nein |

Für E-Mail ein eigenes Postfach nur für Werner anlegen, z. B. bei GMX oder WEB.DE, und dort den SMTP-Zugriff erlauben. Bei Gmail ein App-Passwort verwenden.

### Warum nicht WhatsApp oder Threema?

Automatische Nachrichten erlauben beide nur über **kostenpflichtige Geschäftszugänge**:

- **WhatsApp:** Nur über die WhatsApp Business Platform von Meta. Jede Nachricht kostet einige Cent, dazu kommen ein Geschäftskonto bei Meta, eine eigene Telefonnummer und eine von Meta freigegebene Textvorlage.
- **Threema:** Nur über das Threema Gateway. Eine eigene Absender-ID und jede Nachricht kosten Credits, die man bei Threema kauft.

Kostenlose Umwege über WhatsApp verstoßen gegen dessen Nutzungsbedingungen. Die Nummer kann jederzeit gesperrt werden, und nach Updates fallen solche Lösungen oft aus. Für ein Warnsystem ist das zu unsicher. Werner bleibt deshalb bei Home-Assistant-App, Signal und E-Mail.

## 7. Testen, Updates, Sicherung

- **Testen:** Jeder Vertrauensperson eine Test-Nachricht schicken und kurz nachfragen, ob sie angekommen ist. Einen echten Probealarm nur nach Absprache mit dem Bewohner und den Vertrauenspersonen.
- **Updates:** HACS zeigt neue Werner-Versionen an. Was sich ändert, steht im [Changelog](../../CHANGELOG.md). Nach jedem Update eine Test-Nachricht schicken.
- **Sicherung:** Einstellungen › System › Sicherungen – automatische Sicherung einschalten.
- **Hilfe:** Fragen und Fehler als [Issue](https://github.com/consulting-kleimanns/werner-home-assistant/issues).
