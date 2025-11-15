| Feld-Nr. | Bezeichnung                     | Bedeutung/Funktion                                        | Beispiel                        | Hinweis                                                   |
|----------|----------------------------------|-----------------------------------------------------------|---------------------------------|-----------------------------------------------------------|
| 1        | Satztyp                          | Kennzeichen des Datensatzes (`A` steht für Artikel)       | `A`                             | Immer `A` für Artikeldaten                                |
| 2        | Satzstatus                       | Aktion/Status des Eintrags                                | `N`                             | Im Beispiel `N` (vermutlich „neu“)                        |
| 3        | Artikelnummer                    | Eindeutige Kennung des Artikels                           | `2TOP`                          | Referenz für Suchen und Staffelpreise                     |
| 4        | Artikelbezeichnung               | Hauptbezeichnung                                          | `OMEGA UDOs 330 TopGrip…`       | Bis zu 40 Zeichen                                         |
| 5        | Zusatzbeschreibung               | Details wie Maße oder Verpackung                          | `1,5m x 30 m`                   | Kann leer sein                                             |
| 6        | Mengeneinheit                    | Code der Mengeneinheit                                    | `MTK`                           | Beispiel: MTK = Quadratmeter Karton                       |
| 7        | Preisart-Code                    | 1 = Listenpreis, 2 = Einkaufspreis, 9 = alternative Basis | `2`                             | Zusammenspiel mit Feld 9                                  |
| 8        | Preis-Indikator                  | Technischer Code (im Beispiel `1`)                        | `1`                             | Laut Spezifikation zu prüfen                              |
| 9        | Preis                             | Wert in der Währung der Datei                              | `894`                           | Interpretation abhängig von Feld 7                        |
| 10       | Warengruppe                      | Kategorie/Klasse                                          | `001`                           | Nützlich für Clustering                                   |
| 11       | Kurzgruppe                       | Kürzel der Produktfamilie                                 | `Dac`                           |                                                           |
| 12       | Langgruppe                       | Vollständiger Name der Produktfamilie                     | `Dachbahnen`                    |                                                           |
| 13-18    | Reservierte Felder               | Im Beispiel leer                                          |                                 | Können vom Lieferanten verwendet werden                   |
| 19       | Strichcode/EAN                   | Barcode-Kennung                                           | `9120090200379`                 | Optional                                                  |
| 20       | Zusatzcode                       | Im Beispiel leer                                          |                                 |                                                           |
| 21       | Mehrwertsteuer                   | Steuersatz (in Prozent × 100)                             | `0`                             | `0` = kein bzw. bereits enthalten                         |
| 22       | Mehrwertsteuer-Code              | Im Beispiel leer                                          |                                 |                                                           |
| 23       | Lieferantenrabatt, %             | Rabattwert (falls gesetzt)                                | `0`                             | Bezieht sich auf den Listenpreis                          |
| 24-30    | Reserviert/leer                  | Nicht belegt                                              |                                 | Nutzung abhängig von der Implementierung                 |

> Hinweis: Die Zuordnung basiert auf dem Beispiel `DATANORM.001` sowie den Aufgabenangaben. Felder mit offenem Klärungsbedarf sollten gegen die offizielle DATANORM-Dokumentation des Lieferanten geprüft werden.

