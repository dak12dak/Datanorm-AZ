# Task Description (English)

## Reading the following text file:

- **Specifications**: Text file may contain up to 2 million lines
  - Read into in-memory database
  - Calculate sale price
  - Check if article is available using article number

### Record type A (Article)

- **Field 3** = Article number
- **Field 4** = Article description
- **Field 7** = 1 = List price value, 2 = Purchase price, 9 = List price
  - ⚠ Is the price in field 9 the list price or the purchase price?
- **Field 9** = Price

### Record type Z (Graduated price)

- **Field 3** = Article number
- **Field 8** = 1 = Graduated price, 2 = Surcharge/discount amount, 3 = Percentage surcharge/discount
- **Field 9** = + = Surcharge, - = Discount
- **Field 10** = 1 = List price, 2 = Purchase price
  - ⚠ Is the price/percentage in field 8 the list price or the purchase price?

### Article table structure

**Columns:**
- Article number
- Article description
- List price
- Supplier discount (percent)
- Purchase price
- Overhead (percent)
- Calculated purchase price
- Markup (percent)
- Sale price

