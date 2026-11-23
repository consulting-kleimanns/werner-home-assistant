# Energie (optional)

Die Bildschirme **Energie** und **Auto** zeigen Werte aus Home Assistant und evcc:
- **Netzleistung und Zählerstand:** in der Karten-Option `entities.netz` / `entities.bezug` eintragen (z. B. Tibber Pulse lokal, Shelly, Smart Meter).
- **Sonnen-Tipps:** grobe Schätzung aus der täglichen Wettervorhersage und der Leistung des Balkonkraftwerks (`pv_kwp`). Sie ersetzt keine echte PV-Prognose.
- **Wallbox und Auto:** über [evcc](https://evcc.io). Empfohlener Lademodus für Senioren: „Sonne nutzen, Plan einhalten“ (Min+PV) mit Ladeplan.

Hinweise aus der Praxis:
- Viele Fahrzeug-APIs (z. B. VW seit 2026) liefern Dritten keinen Ladestand mehr. Dann das Auto in evcc als „Fahrzeug ohne Schnittstelle“ anlegen und in kWh planen.
- Kleine Balkonkraftwerke reichen für reines Sonnenladen oft nicht: Dreiphasig laden braucht mindestens rund 4,1 kW.
