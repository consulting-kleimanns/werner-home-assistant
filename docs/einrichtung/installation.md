# Werner installieren und einrichten – für Helfer

Diese Anleitung ist für die Person, die Werner beim Bewohner einrichtet: Angehörige, Nachbarn oder ein Techniker. Für den Bewohner selbst gibt es die Erklärung [So funktioniert Werner](../einfach/so-funktioniert-werner.md).

Richten Sie Werner **gemeinsam mit dem Bewohner** ein. Was der Bewohner selbst entscheidet – wer informiert wird, wann Werner nachfragt, Kamera und Mikrofon – stellt er in seinem Dashboard ein.

> Werner ist kein Hausnotruf und kein Medizinprodukt. Im Notfall gilt immer 112.

Als Helfer erledigen Sie nur die Technik (Schritte 1 bis 5, etwa eine halbe Stunde). Alles, was der Bewohner selbst entscheidet, stellt er danach in **„Mein Zuhause“** ein – am besten mit Ihnen gemeinsam. Eine Liste dort zeigt, was noch fehlt.

## Überblick

| Schritt | Was | Wie oft |
|---|---|---|
| 1 | Home Assistant bereitstellen | einmal |
| 2 | Konto und Handy für jeden Bewohner | je Bewohner |
| 3 | HACS einrichten | einmal |
| 4 | Werner herunterladen | einmal |
| 5 | Signal vorbereiten (empfohlen) | einmal |
| 6 | Werner hinzufügen | einmal |
| 7 | Mit dem Bewohner einrichten | je Bewohner |
| 8 | Testen, Updates, Sicherung | regelmäßig |

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

Über Signal erreicht Werner die Vertrauenspersonen kostenlos und ohne zusätzliche App für sie. Dafür braucht Home Assistant die App „Signal Messenger“. Werner findet sie selbst – eine Adresse müssen Sie nicht eintragen.

1. Einstellungen › Apps › App-Store › ⋮ › Repositories › `https://github.com/haberda/hassio_addons` hinzufügen.
2. **Signal Messenger** installieren.
3. Unter Konfiguration den Modus **json-rpc** wählen und die App starten.
4. Unter **Netzwerk** das Feld für Port 8080 **leer lassen**. Die Schnittstelle hat keine Anmeldung und darf nie aus dem Internet erreichbar sein. Werner spricht sie intern an.

Im Modus `normal` dauert ein QR-Code sehr lange. Verbunden wird später in „Mein Zuhause“ mit dem Signal-Konto des Bewohners (Schritt 7).

## 6. Werner hinzufügen

[![Werner hinzufügen](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=werner)

Oder von Hand: Einstellungen › Geräte & Dienste › Integration hinzufügen › **Werner**.

Der Assistent fragt nur: **Für wen?** Wählen Sie die Person. Den Vornamen und das Handy (die Home-Assistant-App, mit der sich die Person anmeldet) findet Werner selbst. Beides können Sie im selben Fenster ändern.

Danach steht **„Mein Zuhause“** in der Seitenleiste – für jeden Benutzer. Weitere Bewohner müssen Sie nicht im Assistenten anlegen: Jeder schaltet Werner in „Mein Zuhause“ für sich selbst ein, oder ein Bewohner trägt einen anderen ein, der dann selbst zustimmt.

## 7. Mit dem Bewohner einrichten

Melden Sie sich in der Home-Assistant-App des Bewohners an, oder setzen Sie sich mit ihm an ein Tablet. Unter **Einstellen** steht oben „So weit ist Werner eingerichtet“. Jeder offene Punkt führt mit einem Tipp an die richtige Stelle:

- [ ] **Handy** – dort fragt Werner zuerst nach (Reiter „Bewohner“).
- [ ] **Vertrauenspersonen** – bis zu drei, in der gewünschten Reihenfolge, je mit einem Weg (Reiter „Wer & wie“). Danach jeder Person eine Test-Nachricht schicken.
- [ ] **Aktivitätsquellen** – woran Werner merkt, dass der Bewohner aktiv ist (Reiter „Sensoren“). Hinter jedem Gerät stehen Raum und aktueller Wert, z. B. „Küche · gerade: 1,8 kW“. So erkennt man den richtigen Stromzähler leicht.
- [ ] **Signal verbinden** – nur wenn eine Person den Weg Signal hat.

**Signal verbinden braucht zwei Bildschirme.** Der Bewohner scannt den Code mit dem Handy, auf dem sein Signal läuft. Steht „Mein Zuhause“ gerade auf genau diesem Handy, tippt er auf **„Code auf anderem Gerät zeigen“**. Werner zeigt dann einen Link, der auf Computer oder Tablet direkt den Code öffnet. Werner merkt von selbst, wenn es geklappt hat. Werner schreibt danach mit dem Signal des Bewohners; die Vertrauenspersonen sehen ihn als Absender.

Die Regeln „Morgens nichts los“ und „Tagsüber lange still“ arbeiten erst, wenn mindestens eine Aktivitätsquelle gewählt ist – sonst gäbe es Fehlalarme.

Für Helfer gibt es dieselben Einstellungen auch unter Einstellungen › Geräte & Dienste › Werner › **Konfigurieren**.

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
| Signal | kostenlos | ja: Antwort 1, 2 oder 3 |
| E-Mail | kostenlos (eigenes Postfach für Werner) | nein – in der Integration noch in Arbeit |

E-Mail gibt es heute nur im YAML-Paket. Dafür ein eigenes Postfach nur für Werner anlegen, z. B. bei GMX oder WEB.DE, und dort den SMTP-Zugriff erlauben. Bei Gmail ein App-Passwort verwenden.

### Warum nicht WhatsApp oder Threema?

Automatische Nachrichten erlauben beide nur über **kostenpflichtige Geschäftszugänge**:

- **WhatsApp:** Nur über die WhatsApp Business Platform von Meta. Jede Nachricht kostet einige Cent, dazu kommen ein Geschäftskonto bei Meta, eine eigene Telefonnummer und eine von Meta freigegebene Textvorlage.
- **Threema:** Nur über das Threema Gateway. Eine eigene Absender-ID und jede Nachricht kosten Credits, die man bei Threema kauft.

Kostenlose Umwege über WhatsApp verstoßen gegen dessen Nutzungsbedingungen. Die Nummer kann jederzeit gesperrt werden, und nach Updates fallen solche Lösungen oft aus. Für ein Warnsystem ist das zu unsicher. Werner bleibt deshalb bei Home-Assistant-App, Signal und E-Mail.

## 8. Testen, Updates, Sicherung

- **Testen:** Jeder Vertrauensperson eine Test-Nachricht schicken und kurz nachfragen, ob sie angekommen ist. Einen echten Probealarm nur nach Absprache mit dem Bewohner und den Vertrauenspersonen.
- **Updates:** HACS zeigt neue Werner-Versionen an. Was sich ändert, steht im [Changelog](../../CHANGELOG.md). Nach jedem Update eine Test-Nachricht schicken.
- **Sicherung:** Einstellungen › System › Sicherungen – automatische Sicherung einschalten.
- **Hilfe:** Fragen und Fehler als [Issue](https://github.com/consulting-kleimanns/werner-home-assistant/issues).
