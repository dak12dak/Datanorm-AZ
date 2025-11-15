# Task Description (German)

## Einlesen der folgenden Textdatei:

- **Vorgaben**: Textdatei könnte bis zu 2 Millionen Zeilen enthalten
  - Einlesen in fiktive Datenbank
  - Berechnung Verkaufspreis
  - Prüfen ob Artikel bereits vorhanden ist über Artikelnummer

### Satzart A (Artikel)

- **Feld 3** = Artikelnummer
- **Feld 4** = Artikelbezeichnung
- **Feld 7** = 1 = Wert Listenpreis, 2 = Einkaufspreis, 9 = Listenpreis
  - ⚠ Ist der Preis in Feld 9 der Listenpreis oder der Einkaufspreis?
- **Feld 9** = Preis

### Satzart Z (Staffelpreis)

- **Feld 3** = Artikelnummer
- **Feld 8** = 1 = Staffelpreis, 2 = Zu/Abschlag Betrag, 3 = prozentueller Zu/Abschlag
- **Feld 9** = + = Zuschlag, - = Abschlag
- **Feld 10** = 1 = Listenpreis, 2 = Einkaufspreis
  - ⚠ Ist der Preis/Prozentsatz in Feld 8 der Listenpreis oder der Einkaufspreis?

### Aufbau Artikel-Tabelle

**Spalten:**
- Artikelnummer
- Artikelbezeichnung
- Listenpreis
- Lieferantenrabatt (Prozent)
- Einkaufspreis
- Gemeinkosten (Prozent)
- Kalk. Einkaufspreis
- Aufschlag (Prozent)
- Verkaufspreis

