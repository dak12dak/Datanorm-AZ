# Antworten auf Fragen

## Frage 1: Datensatztyp A (Artikel)

**Frage:** Ist der Preis in Feld 9 der Listenpreis oder der Einkaufspreis?

**Antwort:** Es hängt von Feld 7 (Preistyp-Code) ab:
- Wenn Feld 7 = 1 oder 9 → Feld 9 enthält den **Listenpreis**
- Wenn Feld 7 = 2 → Feld 9 enthält den **Einkaufspreis**

Feld 7 Werte:
- `1` = Listenpreis (прейскурантная)
- `2` = Einkaufspreis (закупочная)
- `9` = Alternativer Preis (альтернативная)

**Hinweis:** Da die Spezifikation nicht klar definiert, was "alternativer Preis" (Wert 9) bedeutet, behandeln wir ihn in unserer Implementierung als **Listenpreis**.

Die Interpretation ist im Code wie folgt implementiert:
- Wenn `price_type` (Feld 7) `1` oder `9` ist, wird `price_value` (Feld 9) als Listenpreis behandelt
- Wenn `price_type` (Feld 7) `2` ist, wird `price_value` (Feld 9) als Einkaufspreis behandelt

---

## Frage 2: Datensatztyp Z (Staffelpreis)

**Frage:** Bezieht sich der Preis/Prozentsatz in Feld 8 auf den Listenpreis oder den Einkaufspreis?

**Antwort:** Feld 8 ist der **Werttyp**, nicht der Preis selbst. Der tatsächliche Preis/Prozentsatz befindet sich in Feld 12 (Wert). Die Basis (Listenpreis oder Einkaufspreis) wird durch **Feld 10** (Preisbasis) bestimmt:
- Wenn Feld 10 = 1 → bezieht sich der Preis/Prozentsatz in Feld 12 auf den **Listenpreis**
- Wenn Feld 10 = 2 → bezieht sich der Preis/Prozentsatz in Feld 12 auf den **Einkaufspreis**

Feldbedeutungen:
- **Feld 8** = Werttyp:
  - `1` = Staffelpreis
  - `2` = Zuschlag/Rabatt absoluter Betrag
  - `3` = Prozentsatz Zuschlag/Rabatt
- **Feld 10** = Preisbasis:
  - `1` = Listenpreis
  - `2` = Einkaufspreis
- **Feld 12** = Wert (Preis/Betrag/Prozentsatz gemäß Feld 8)

Die Basis wird also durch Feld 10 bestimmt, nicht durch Feld 8.

