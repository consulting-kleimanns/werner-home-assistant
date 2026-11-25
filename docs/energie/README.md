# Energie (optional)

Die Bildschirme **Energie** und **Auto** zeigen Werte aus Home Assistant und evcc. Was angezeigt wird, wählt der Bewohner selbst: Energie › **„Was hier angezeigt wird – ändern“**. Hinter jedem Gerät steht dort der Wert von gerade eben, damit man den richtigen Sensor erkennt. Felder ohne Auswahl werden ausgeblendet.

- **Strom aus dem Netz und Zählerstand:** Leistungs- und Energiesensor des Stromzählers (z. B. Tibber Pulse lokal, Shelly, Smart Meter).
- **Sonnenstrom und Batterie:** Leistung des Balkonkraftwerks bzw. Ladestand der Batterie.
- **Sonnen-Tipps:** grobe Schätzung aus der täglichen Wettervorhersage und der Größe der Anlage in kWp. Sie ersetzt keine echte PV-Prognose.
- **Wallbox und Auto:** über [evcc](https://evcc.io). Ladestand des Autos und der Lademodus (Auswahl-Entität der evcc-Integration). Empfohlener Lademodus für Senioren: „Sonne nutzen, Plan einhalten“ (Min+PV) mit Ladeplan.

## Diagramme „Strom heute und morgen“

Unter Energie zeigt Werner bis zu drei Diagramme. Jedes erscheint nur, wenn die Quelle da ist:

| Diagramm | Zeitraum | Quelle | Einrichtung (einmal durch einen Helfer) |
|---|---|---|---|
| **Strompreis** je Stunde, grün = günstig, rot = teuer | 6 Std. zurück bis 24 Std. voraus | eingebaute Integration **Nord Pool** (Börsenpreis, kein Konto nötig) | Einstellungen › Geräte & Dienste › „Nord Pool“ hinzufügen, Gebiet *Germany*, Währung *EUR*. Die Preise für morgen kommen gegen 13 Uhr. |
| **Sonnenstrom-Vorhersage** in kWh je Stunde | jetzt bis 24 Std. voraus | eingebaute Integration **Forecast.Solar** | macht der Bewohner selbst: Energie › „Was hier angezeigt wird – ändern“ › **Ihre Solaranlage** (Leistung in Watt, Himmelsrichtung, Aufstellung). Werner legt den Eintrag am Standort des Zuhauses an. Ein vorhandener Forecast.Solar-Eintrag wird ebenfalls erkannt. |
| **Stromverbrauch der Wohnung**, verbraucht und erwartet | 12 Std. zurück, 6 Std. voraus | Statistik des gewählten **Zählerstands** | nichts weiter – die Erwartung ist der Durchschnitt derselben Uhrzeit an den letzten bis zu 14 Tagen. Sie wird mit jedem Tag genauer. |

Der Börsenpreis ist nicht der Preis auf der Stromrechnung. Unter „Was hier angezeigt wird – ändern“ lässt sich deshalb die Mehrwertsteuer zuschalten (Standard: an) und ein fester **Aufschlag in Cent je kWh** für Netzentgelt, Abgaben und Anbieter eintragen. Dann heißt die Kurve „Ihr Strompreis (geschätzt)“. Beides lässt sich dort auch abschalten („– nicht zeigen –“).

Hinweise aus der Praxis:
- Viele Fahrzeug-APIs (z. B. VW seit 2026) liefern Dritten keinen Ladestand mehr. Dann das Auto in evcc als „Fahrzeug ohne Schnittstelle“ anlegen und in kWh planen.
- Kleine Balkonkraftwerke reichen für reines Sonnenladen oft nicht: Dreiphasig laden braucht mindestens rund 4,1 kW.
