| Column          | Description                    | Data Type | Source            | Example              |
|-----------------|--------------------------------|-----------|-------------------|---------------------|
| step_code       | Step code                      | TEXT      | Field 4 from record Z | 01                  |
| description     | Step description               | TEXT      | Field 6 from record Z | Staffelpr. 45 bis 899 |
| price_kind      | Value type                     | INTEGER   | Field 8 from record Z | 1                   |
| sign            | Surcharge/discount sign        | TEXT      | Field 9 from record Z | +                   |
| base_price_type | Price base                     | INTEGER   | Field 10 from record Z | 2                   |
| value           | Value                          | REAL      | Field 12 from record Z | 626.0               |
| min_quantity    | Minimum quantity               | REAL      | Field 15 from record Z | 45.0                |
| max_quantity    | Maximum quantity               | REAL      | Field 16 from record Z | 899.0               |

**Notes:**

`price_kind`: `1` = Graduated price, `2` = Surcharge/discount absolute, `3` = Percent.

`sign`: `+` = Surcharge, `-` = Discount.

`base_price_type`: `1` = List price, `2` = Purchase price.

`min_quantity` and `max_quantity` define the quantity range for which this price applies.

