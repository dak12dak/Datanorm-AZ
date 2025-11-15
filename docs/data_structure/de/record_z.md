| Feld-Nr. | Bezeichnung                      | Bedeutung/Funktion                                               | Beispiel                      | Hinweis                                                        |
|----------|----------------------------------|------------------------------------------------------------------|-------------------------------|----------------------------------------------------------------|
| 1        | Satztyp                          | Kennzeichen `Z` für Staffel-/Konditionssatz                      | `Z`                           | Immer `Z`                                                       |
| 2        | Satzstatus                       | Aktionsflag                                                       | `N`                           | Häufig `N` = neu                                                |
| 3        | Artikelnummer                    | Verweis auf Artikel (Feld 3 aus Datensatz `A`)                   | `2TOP`                        | Verknüpfung mit Artikeldaten                                   |
| 4        | Staffelcode                      | Identifikator der Preisstufe                                     | `01`                          | Laufende Nummer                                                |
| 5        | Konditionsnummer                 | Oft fix (`1`)                                                     | `1`                           | Laut Spezifikation zu prüfen                                   |
| 6        | Kurzbeschreibung der Stufe       | Bezeichnung des Mengenintervalls                                 | `Staffelpr. 45 bis 899`       |                                                                |
| 7        | Langbeschreibung der Stufe       | Ergänzung zu Feld 6                                               | `Staffelpr. 45 bis 899`       |                                                                |
| 8        | Werttyp                          | `1` = Staffelpreis, `2` = Zuschlag/Abschlag absolut, `3` = Prozent | `1`                           | Im Beispiel immer `1`                                          |
| 9        | Vorzeichen                       | `+` = Zuschlag, `-` = Abschlag                                    | `+`                           |                                                                |
| 10       | Preisbasis                       | `1` = Listenpreis, `2` = Einkaufspreis                            | `2`                           | Bestimmt die Bezugsbasis                                       |
| 11       | Mengeneinheit Bedingung          | Häufig `1` (Stück)                                                | `1`                           |                                                                |
| 12       | Wert                              | Preis/Summe/Prozent gemäß Feld 8                                  | `626`                         | Bei Typ 1 = Endpreis in Währung                                |
| 13       | Reserviert                       | Im Beispiel leer                                                  |                               |                                                                |
| 14       | Mengeneinheit Staffel            | Einheit des Mengenbereichs                                       | `1`                           |                                                                |
| 15       | Mindestmenge                     | Untere Grenze                                                     | `45`                          |                                                                |
| 16       | Maximalmenge                     | Obere Grenze                                                      | `899`                         | Große Werte ≈ „unbegrenzt nach oben“                           |
| 17       | Reserviert/leer                  | Im Beispiel nicht belegt                                          |                               |                                                                |

> Hinweis: Die Zuordnung basiert auf `DATANORM.001`. Für verbindliche Bedeutungen (z. B. Felder 5 und 11) ist die offizielle DATANORM-Dokumentation maßgeblich.

