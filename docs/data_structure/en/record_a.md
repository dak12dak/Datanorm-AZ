| Field No. | Name                              | Meaning/Function                                        | Example                        | Note                                                       |
|----------|----------------------------------|-----------------------------------------------------------|---------------------------------|-----------------------------------------------------------|
| 1        | Record type                       | Record identifier (`A` stands for Article)               | `A`                             | Always `A` for article data                                |
| 2        | Record status                     | Action/Status of the entry                               | `N`                             | In example `N` (likely "new")                              |
| 3        | Article number                    | Unique article identifier                                | `2TOP`                          | Reference for searching and graduated prices                |
| 4        | Article description               | Main description                                         | `OMEGA UDOs 330 TopGrip…`       | Up to 40 characters                                        |
| 5        | Additional description            | Details such as dimensions or packaging                  | `1,5m x 30 m`                   | May be empty                                                |
| 6        | Unit of measure                   | Unit code                                                | `MTK`                           | Example: MTK = square meters cardboard                      |
| 7        | Price type code                   | 1 = List price, 2 = Purchase price, 9 = alternative base | `2`                             | Works together with field 9                                 |
| 8        | Price indicator                   | Technical code (in example `1`)                          | `1`                             | To be verified according to specification                   |
| 9        | Price                             | Value in file currency                                   | `894`                           | Interpretation depends on field 7                           |
| 10       | Product group                     | Category/class                                           | `001`                           | Useful for clustering                                       |
| 11       | Short group                       | Product family abbreviation                              | `Dac`                           |                                                            |
| 12       | Long group                        | Full product family name                                 | `Dachbahnen`                    |                                                            |
| 13-18    | Reserved fields                   | Empty in example                                         |                                 | May be used by supplier                                     |
| 19       | Barcode/EAN                       | Barcode identifier                                       | `9120090200379`                 | Optional                                                    |
| 20       | Additional code                   | Empty in example                                         |                                 |                                                            |
| 21       | VAT                               | Tax rate (in percent × 100)                              | `0`                             | `0` = none or already included                              |
| 22       | VAT code                          | Empty in example                                         |                                 |                                                            |
| 23       | Supplier discount, %              | Discount value (if set)                                  | `0`                             | Refers to list price                                        |
| 24-30    | Reserved/empty                    | Not used                                                 |                                 | Usage depends on implementation                            |

> Note: The mapping is based on the example `DATANORM.001` and task specifications. Fields with open clarification needs should be verified against the official DATANORM documentation from the supplier.


