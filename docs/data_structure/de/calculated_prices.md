# Struktur der berechneten Preise (Ausgabe)

Dieses Dokument beschreibt die Struktur der Ausgabe, die von der Methode `calculate_prices()` zurückgegeben und von `export_prices_to_csv()` exportiert wird.

Jede Zeile stellt ein Wörterbuch mit den folgenden Feldern dar (alle Preise sind Stückpreise):

| Spalte                     | Beschreibung                         | Datentyp | Quelle                                     | Beispiel |
|----------------------------|--------------------------------------|----------|--------------------------------------------|----------|
| article_no                 | Artikelnummer                        | TEXT     | Feld 3 aus Datensatz A                     | 2TOP     |
| name                       | Artikelbezeichnung                   | TEXT     | Feld 4 aus Datensatz A                     | OMEGA UDOs… |
| unit                       | Mengeneinheit                        | TEXT     | Feld 6 aus Datensatz A                     | MTK      |
| list_price                 | Listenpreis                          | REAL     | Preis aus Typ 1/9 oder Staffel base=1      | 894.0    |
| supplier_discount_pct      | Lieferantenrabatt, %                 | REAL     | Berechnung                                 | 29.87    |
| purchase_price             | Einkaufspreis                        | REAL     | Preis aus Typ 2 oder Staffel base=2        | 626.0    |
| overhead_pct               | Gemeinkosten, %                      | REAL     | Laufzeitparameter                          | 0.0      |
| calculated_purchase_price  | Berechneter Einkaufspreis            | REAL     | purchase_price × (1 + overhead/100)        | 626.0    |
| markup_pct                 | Aufschlag, %                         | REAL     | Berechnung                                 | 42.59    |
| sale_price                 | Verkaufspreis                        | REAL     | list_price oder calculated_purchase        | 894.0    |

**Zusätzliche Felder bei Angabe der Menge:**

Wenn der Parameter `quantity` an `calculate_prices()` oder `export_prices_to_csv()` übergeben wird, werden die folgenden zusätzlichen Felder einbezogen:

| Spalte                     | Beschreibung                         | Datentyp | Quelle                                     | Beispiel |
|----------------------------|--------------------------------------|----------|--------------------------------------------|----------|
| quantity                   | Angegebene Menge für Preisberechnung | REAL     | Laufzeitparameter                          | 200.0    |
| total_list_price           | Gesamtlistenpreis (list_price × quantity) | REAL  | Berechnung                                | 178800.0 |
| total_purchase_price       | Gesamteinkaufspreis (purchase_price × quantity) | REAL | Berechnung                        | 125200.0 |
| total_calculated_purchase_price | Gesamtberechneter Einkaufspreis (calculated_purchase_price × quantity) | REAL | Berechnung | 125200.0 |
| total_sale_price           | Gesamtverkaufspreis (sale_price × quantity) | REAL | Berechnung                            | 178800.0 |


