# Answers to Questions

## Question 1: Record type A (Article)

**Question:** Is the price in field 9 the list price or the purchase price?

**Answer:** It depends on field 7 (Price type code):
- If field 7 = 1 or 9 → field 9 contains **list price**
- If field 7 = 2 → field 9 contains **purchase price**

Field 7 values:
- `1` = List price (прейскурантная)
- `2` = Purchase price (закупочная)
- `9` = Alternative price (альтернативная)

**Note:** Since the specification does not clearly define what "alternative price" (value 9) means, we treat it as **list price** in our implementation.

The interpretation is implemented in the code as follows:
- When `price_type` (field 7) is `1` or `9`, the `price_value` (field 9) is treated as list price
- When `price_type` (field 7) is `2`, the `price_value` (field 9) is treated as purchase price

---

## Question 2: Record type Z (Graduated price)

**Question:** Is the price/percentage in field 8 the list price or the purchase price?

**Answer:** Field 8 is the **value type**, not the price itself. The actual price/percentage is in field 12 (Value). The base (list price or purchase price) is determined by **field 10** (Price base):
- If field 10 = 1 → the price/percentage in field 12 refers to **list price**
- If field 10 = 2 → the price/percentage in field 12 refers to **purchase price**

Field meanings:
- **Field 8** = Value type:
  - `1` = Graduated price
  - `2` = Surcharge/discount absolute amount
  - `3` = Percentage surcharge/discount
- **Field 10** = Price base:
  - `1` = List price
  - `2` = Purchase price
- **Field 12** = Value (price/amount/percentage according to field 8)

So the base is determined by field 10, not field 8.

