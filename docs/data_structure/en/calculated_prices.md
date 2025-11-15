# Calculated Prices Output Structure

This document describes the structure of the output returned by `calculate_prices()` method and exported by `export_prices_to_csv()`.

Each row represents a dictionary with the following fields (all prices are unit prices):

| Column                      | Description                         | Data Type | Source                                     | Example |
|----------------------------|--------------------------------------|----------|--------------------------------------------|----------|
| article_no                 | Article number                       | TEXT     | Field 3 from record A                      | 2TOP     |
| name                       | Article description                  | TEXT     | Field 4 from record A                      | OMEGA UDOs… |
| unit                       | Unit of measure                      | TEXT     | Field 6 from record A                      | MTK      |
| list_price                 | List price                           | REAL     | Price from type 1/9 or step base=1         | 894.0    |
| supplier_discount_pct      | Supplier discount, %                 | REAL     | Calculation                                | 29.87    |
| purchase_price             | Purchase price                       | REAL     | Price from type 2 or step base=2           | 626.0    |
| overhead_pct               | Overhead, %                          | REAL     | Runtime parameter                          | 0.0      |
| calculated_purchase_price  | Calculated purchase price            | REAL     | purchase_price × (1 + overhead/100)        | 626.0    |
| markup_pct                 | Markup, %                            | REAL     | Calculation                                | 42.59    |
| sale_price                 | Sale price                           | REAL     | list_price or calculated_purchase          | 894.0    |

**Additional fields when quantity is specified:**

When `quantity` parameter is provided to `calculate_prices()` or `export_prices_to_csv()`, the following additional fields are included:

| Column                      | Description                         | Data Type | Source                                     | Example |
|----------------------------|--------------------------------------|----------|--------------------------------------------|----------|
| quantity                    | Specified quantity for price calculation | REAL   | Runtime parameter                          | 200.0    |
| total_list_price            | Total list price (list_price × quantity) | REAL  | Calculation                                | 178800.0 |
| total_purchase_price        | Total purchase price (purchase_price × quantity) | REAL | Calculation                        | 125200.0 |
| total_calculated_purchase_price | Total calculated purchase price (calculated_purchase_price × quantity) | REAL | Calculation | 125200.0 |
| total_sale_price            | Total sale price (sale_price × quantity) | REAL | Calculation                            | 178800.0 |


