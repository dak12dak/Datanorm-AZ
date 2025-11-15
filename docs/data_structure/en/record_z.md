| Field No. | Name                              | Meaning/Function                                               | Example                      | Note                                                        |
|----------|----------------------------------|------------------------------------------------------------------|-------------------------------|----------------------------------------------------------------|
| 1        | Record type                       | Identifier `Z` for graduated/condition record                   | `Z`                           | Always `Z`                                                    |
| 2        | Record status                     | Action flag                                                      | `N`                           | Often `N` = new                                                |
| 3        | Article number                    | Reference to article (Field 3 from record `A`)                   | `2TOP`                        | Link to article data                                          |
| 4        | Step code                         | Price step identifier                                            | `01`                          | Sequential number                                             |
| 5        | Condition number                  | Often fixed (`1`)                                                 | `1`                           | To be verified according to specification                     |
| 6        | Short description of step         | Quantity interval description                                    | `Staffelpr. 45 bis 899`       |                                                               |
| 7        | Long description of step          | Supplement to field 6                                            | `Staffelpr. 45 bis 899`       |                                                               |
| 8        | Value type                        | `1` = Graduated price, `2` = Surcharge/discount absolute, `3` = Percent | `1`                           | In example always `1`                                          |
| 9        | Sign                              | `+` = Surcharge, `-` = Discount                                  | `+`                           |                                                               |
| 10       | Price base                        | `1` = List price, `2` = Purchase price                           | `2`                           | Determines the reference base                                 |
| 11       | Unit of measure condition         | Often `1` (piece)                                                 | `1`                           |                                                               |
| 12       | Value                             | Price/sum/percent according to field 8                           | `626`                         | For type 1 = final price in currency                          |
| 13       | Reserved                          | Empty in example                                                  |                               |                                                               |
| 14       | Unit of measure step              | Unit of quantity range                                           | `1`                           |                                                               |
| 15       | Minimum quantity                  | Lower limit                                                      | `45`                          |                                                               |
| 16       | Maximum quantity                  | Upper limit                                                      | `899`                         | Large values ≈ "unlimited upward"                            |
| 17       | Reserved/empty                    | Not used in example                                               |                               |                                                               |

> Note: The mapping is based on `DATANORM.001`. For binding meanings (e.g. fields 5 and 11), the official DATANORM documentation is authoritative.


