# Energie (optional)

Die Bildschirme **Energie** und **Auto** zeigen Werte aus Home Assistant und evcc. Was angezeigt wird, wählt der Bewohner selbst: Energie › **„Was hier angezeigt wird – ändern“**. Hinter jedem Gerät steht dort der Wert von gerade eben, damit man den richtigen Sensor erkennt. Felder ohne Auswahl werden ausgeblendet.

- **Strom aus dem Netz und Zählerstand:** Leistungs- und Energiesensor des Stromzählers (z. B. Tibber Pulse lokal, Shelly, Smart Meter).
- **Sonnenstrom und Batterie:** Leistung des Balkonkraftwerks bzw. Ladestand der Batterie.
- **Sonnen-Tipps:** grobe Schätzung aus der täglichen Wettervorhersage und der Größe der Anlage in kWp. Sie ersetzt keine echte PV-Prognose.
- **Wallbox und Auto:** über [evcc](https://evcc.io). Ladestand des Autos und der Lademodus (Auswahl-Entität der evcc-Integration). Empfohlener Lademodus für Senioren: „Sonne nutzen, Plan einhalten“ (Min+PV) mit Ladeplan.

Hinweise aus der Praxis:
- Viele Fahrzeug-APIs (z. B. VW seit 2026) liefern Dritten keinen Ladestand mehr. Dann das Auto in evcc als „Fahrzeug ohne Schnittstelle“ anlegen und in kWh planen.
- Kleine Balkonkraftwerke reichen für reines Sonnenladen oft nicht: Dreiphasig laden braucht mindestens rund 4,1 kW.
