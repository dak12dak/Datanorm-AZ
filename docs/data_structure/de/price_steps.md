| Spalte          | Beschreibung                   | Datentyp | Quelle            | Beispiel            |
|-----------------|--------------------------------|----------|-------------------|---------------------|
| step_code       | Staffelcode                    | TEXT     | Feld 4 aus Datensatz Z | 01                  |
| description     | Stufenbeschreibung             | TEXT     | Feld 6 aus Datensatz Z | Staffelpr. 45 bis 899 |
| price_kind      | Werttyp                        | INTEGER  | Feld 8 aus Datensatz Z | 1                   |
| sign            | Vorzeichen Zuschlag/Abschlag   | TEXT     | Feld 9 aus Datensatz Z | +                   |
| base_price_type | Preisbasis                     | INTEGER  | Feld 10 aus Datensatz Z | 2                   |
| value           | Wert                           | REAL     | Feld 12 aus Datensatz Z | 626.0               |
| min_quantity    | Mindestmenge                   | REAL     | Feld 15 aus Datensatz Z | 45.0                |
| max_quantity    | Höchstmenge                    | REAL     | Feld 16 aus Datensatz Z | 899.0               |

**Hinweise:**

`price_kind`: `1` = Staffelpreis, `2` = Zuschlag/Abschlag absolut, `3` = Prozent.

`sign`: `+` = Zuschlag, `-` = Abschlag.

`base_price_type`: `1` = Listenpreis, `2` = Einkaufspreis.

`min_quantity` und `max_quantity` definieren den Mengenbereich, für den dieser Preis gilt.

