# Datanorm-AZ

![Python](https://img.shields.io/badge/Python-3.7+-blue)
![SQLite](https://img.shields.io/badge/SQLite-3.x-lightgrey)

A cross-platform Python tool for parsing DATANORM files (record types A and Z), loading data into an in-memory database, and calculating sales prices with overhead and markup calculations.

## Features

- Parse DATANORM format files (up to 2 million lines), consisting of records A and Z
- Create in-memory SQLite database, storing article data (type A) and graduated prices (type Z)
- Calculate derived price information:
  - List prices and purchase prices (with quantity-based graduated pricing support)
  - Supplier discounts
  - Calculated purchase prices with overhead
  - Markup percentages
  - Final sale prices (based on quantity if specified)
- Look up individual articles with all price steps
- Export calculated prices to CSV
- Display output with SQL-style formatting

## Installation

Requires Python 3.7+ only. All required modules are part of the standard library:

- `argparse` - command-line argument parsing
- `csv` - CSV file handling
- `json` - JSON serialization
- `sqlite3` - in-memory database
- `pathlib` - path handling
- `dataclasses` - data classes
- `typing` - type hints
- `__future__` - future features

No external dependencies or installation required.

## Configuration

The input DATANORM file can be specified in `config.py`. Default setup:

```python
datafile = "docs/task_description/DATANORM.001"
```

## Usage

### Basic Usage

Process input DATANORM file and display both article information and calculated prices for the first article:
```bash
python main.py
```

Output:
```json
{
  "article": {
                   "article_no": "2AIRDB",
                         "name": "AIRSTOP SD18 Dampfbremse 1,50 x 50 m",
                         "unit": "MTK",
                   "list_price": 231.0,
               "purchase_price": null,
          "availability_status": "Article found, stock level unknown",
                  "price_steps": [...]
  },
   "prices": {
                   "article_no": "2AIRDB",
                         "name": "AIRSTOP SD18 Dampfbremse 1,50 x 50 m",
                         "unit": "MTK",
                   "list_price": 231.0,
        "supplier_discount_pct": 29.87,
               "purchase_price": 162.0,
                 "overhead_pct": 0.0,
    "calculated_purchase_price": 162.0,
                   "markup_pct": 42.59,
                   "sale_price": 231.0
  }
}
```

Where:

- `supplier_discount_pct` = `(1 - purchase_price / list_price) * 100`
- `calculated_purchase_price` = `purchase_price * (1 + overhead_pct / 100)`
- `markup_pct` = `(sale_price / calculated_purchase_price - 1) * 100`
- `sale_price` = `list_price` or `calculated_purchase_price` (whichever is available)
- Prices are selected from graduated price steps based on quantity (default quantity = 1)
- All calculated prices and percentages are rounded to the number of decimal digits specified in `config.py` (`ROUND_TO_DEC_DIGIT`, default: 2)

### Lookup Specific Article

Get detailed information about a single article (raw data without price calculations):
```bash
python main.py --article 2TOP
```

The command returns JSON with article details and all associated price steps (raw data from database, no calculated fields).

### Get Calculated Prices for Specific Article

Get calculated prices for a single article. Prices are calculated based on graduated price steps. Use `--qnt` to specify quantity for quantity-based pricing (default quantity = 1):
```bash
python main.py --prices 2TOP
python main.py --prices 2TOP --qnt 100  # Calculate prices for quantity 100
```

The command returns JSON array with calculated price fields. Prices are selected from graduated price steps based on the specified quantity (or quantity = 1 by default).

**Note:** When `--qnt` is specified, the output includes both unit prices (per item) and total prices (unit price × quantity). When `--qnt` is not specified, only unit prices are returned.

### Limit Output

Display first N articles (default is 1). Use the `--limit` option with `{None|all}` for unlimited:
```bash
python main.py --limit 10
python main.py --limit {None|all}  # Show all articles
```

### Overhead Percentage

Apply overhead percentage to purchase prices:
```bash
python main.py --overhead 10.0
```

### Export to CSV

Export calculated prices to a CSV file:
```bash
python main.py --export output.csv                 # Export calculated prices for first article (default limit=1)
python main.py --export output.csv --limit all     # Export calculated prices for all articles
python main.py --export output.csv --limit 10      # Export calculated prices for first 10 articles
python main.py --export output.csv --article 2TOP  # Export calculated prices for specific article (quantity = 1)
python main.py --export output.csv --article 2TOP --qnt 100  # Export calculated prices for specific article with quantity-based pricing (includes total prices)
```

### Custom DATANORM File

Process a different DATANORM file:
```bash
python main.py path/to/file.dat
```

**Note:** Only record types A (articles) and Z (graduated prices) are processed. All other record types are ignored.

**File Encoding Support:**

The processor supports various text encodings for DATANORM files:

- **Default**: `latin-1` (ISO-8859-1)
- **UTF-8**: For files with Unicode characters (e.g., Russian, German umlauts)
- **Windows-1251**: For Cyrillic characters (Russian, Bulgarian, etc.)
- **Other encodings**: Any encoding supported by Python's `open()` function

Default encodings can be configured in `config.py`: `default_input_encoding` for DATANORM files and `default_output_encoding` for CSV export.

Rounding precision for calculated prices and percentages can be configured in `config.py`: `ROUND_TO_DEC_DIGIT` (default: 2 decimal digits).

## Limitations

The following features are **not currently supported**:

- **Multiple articles with different quantities in a single request**: You can specify only one article number (`--article` or `--prices`) and one quantity (`--qnt`) per command. To process multiple articles with different quantities, you need to run separate commands for each article-quantity combination.

## Project Structure

```
.
├── config.py               # Configuration settings
├── datanorm_parser.py      # CLI argument parser
├── datanorm_processor.py   # Core processing logic
├── json_formatter.py       # JSON formatting utilities
├── main.py                 # Main entry point
│
├── docs/                   # Documentation
│   │
│   ├── cli_main_py/        # CLI main module documentation
│   │   ├── cli_logic.md    # CLI logic documentation with diagram and description
│   │   ├── cli_logic_chart.mmd  # CLI logic decision flowchart (Mermaid source)
│   │   └── cli_logic_chart.svg  # CLI logic decision flowchart (SVG)
│   │
│   ├── data_structure/     # Data structure documentation
│   │   │
│   │   ├── de/             # German documentation
│   │   │   ├── calculated_prices.md/html  # Output structure
│   │   │   ├── price_steps.md/html        # Price steps structure
│   │   │   ├── record_a.md/html           # Record type A
│   │   │   └── record_z.md/html           # Record type Z
│   │   │
│   │   ├── en/             # English documentation
│   │   │   ├── calculated_prices.md/html  # Output structure
│   │   │   ├── price_steps.md/html        # Price steps structure
│   │   │   ├── record_a.md/html           # Record type A
│   │   │   └── record_z.md/html           # Record type Z
│   │   │
│   │   └── ru/             # Russian documentation
│   │       ├── calculated_prices.md/html  # Output structure
│   │       ├── price_steps.md/html        # Price steps structure
│   │       ├── record_a.md/html           # Record type A
│   │       └── record_z.md/html           # Record type Z
│   │
│   └── task_description/   # Task files and test data
│       │
│       ├── DATANORM.001    # Test DATANORM file
│       │
│       ├── de/             # German documentation
│       │   ├── task.md/html        # Task description
│       │   └── answers.md/html     # Answers to questions
│       │
│       ├── en/             # English documentation
│       │   ├── task.md/html        # Task description
│       │   └── answers.md/html     # Answers to questions
│       │
│       └── ru/             # Russian documentation
│           ├── task.md/html        # Task description
│           └── answers.md/html     # Answers to questions
│
├── tools/                  # Utility tools
│   ├── extract_mmd.py      # Mermaid diagram extractor
│   ├── html_mmd2svg.py     # Replace Mermaid blocks with SVG images in HTML
│   ├── md2html.py          # Markdown to HTML converter
│   └── mmd2svg.py          # Mermaid diagram to SVG converter
│
└── untst/                  # Unit tests
    ├── test_datanorm_parser.py     # Tests for datanorm_parser
    ├── test_datanorm_processor.py  # Tests for datanorm_processor
    ├── test_extract_mmd.py         # Tests for extract_mmd tool
    ├── test_html_mmd2svg.py        # Tests for html_mmd2svg tool
    ├── test_main.py                # Tests for main module
    ├── test_md2html.py             # Tests for md2html tool
    └── test_mmd2svg.py             # Tests for mmd2svg tool
```

## DATANORM Format

The processor handles DATANORM format files with:

- **Record type A**: [Article master data](docs/data_structure/en/record_a.md) (product information, prices)
- **Record type Z**: [Graduated prices](docs/data_structure/en/record_z.md) (quantity-based pricing steps)

See `docs/data_structure/` for detailed field documentation (available in German, Russian, and English):

- [Calculated prices output structure](docs/data_structure/en/calculated_prices.md) - Structure of `calculate_prices()` output
- [Price steps structure](docs/data_structure/en/price_steps.md) - Structure of price steps returned by `lookup_article()`

## Algorithm

The processor follows a streaming approach to efficiently handle large DATANORM files:

1. **Database Initialization**: Create an in-memory SQLite database with `articles` and `price_steps` tables
2. **File Parsing**: Read DATANORM file line by line, identify record types (A for articles, Z for price steps), and parse semicolon-separated fields
3. **Data Storage**: Use upsert operations (INSERT ... ON CONFLICT DO UPDATE) to store/update records
4. **Price Calculation**: Calculate derived prices using base prices, quantity-based pricing, overhead, discounts, and markup
5. **Output Generation**: Format as JSON (default) or export to CSV (output folder is created automatically if needed)

### Price Calculation Details and Edge Cases

#### Price Resolution Priority

When prices are available from multiple sources, the following priority is used:

1. **Quantity-specific price from price steps** (if quantity is specified and matches a price step range)
2. **Price from article record (type A)** (if available)
3. **First price from price steps** (lowest quantity range, as fallback)

**Example:** If an article has:
- List price in article record (A): 100.0
- Price step (Z) for quantity 50-99: 90.0
- Price step (Z) for quantity 100+: 80.0

Then:

- `--qnt 75` → uses 90.0 (from price step matching quantity range)
- `--qnt 1` → uses 100.0 (from article record, no matching price step)
- If article record had no price → would use 90.0 (first price step)

#### Missing Prices

**When list price is missing:**

- Falls back to price steps (if available)
- If still missing, `sale_price` uses `calculated_purchase_price` instead
- `supplier_discount_pct` is `null` (cannot calculate without both prices)

**When purchase price is missing:**

- Falls back to price steps (if available)
- If still missing, `calculated_purchase_price` is `null`
- `markup_pct` is `null` (cannot calculate without `calculated_purchase_price`)
- `sale_price` uses `list_price` if available

**Example with missing purchase price:**
```json
{
  "list_price": 894.0,
  "purchase_price": null,
  "supplier_discount_pct": null,
  "calculated_purchase_price": null,
  "sale_price": 894.0,
  "markup_pct": null
}
```

#### Quantity-Based Pricing

Price steps are selected based on the quantity falling within the `min_quantity` and `max_quantity` range:

- If quantity matches a range → use that price step's value
- If quantity is below all ranges → use first (lowest) price step
- If quantity is above all ranges → use last (highest) price step
- If no price steps exist → use price from article record

**Example:** Article has price steps:
- Quantity 1-49: 100.0
- Quantity 50-99: 90.0
- Quantity 100+: 80.0

Results:

- `--qnt 25` → 100.0 (within 1-49 range) - unit price
- `--qnt 75` → 90.0 (within 50-99 range) - unit price
- `--qnt 150` → 80.0 (within 100+ range) - unit price
- `--qnt 0.5` → 100.0 (below all ranges, uses first step) - unit price

**Total Prices:** When `--qnt` is specified, the output includes both unit prices (per item) and total prices (unit price × quantity). For example, with `--qnt 200` and unit price 162.0, the output will include:
- `purchase_price: 162.0` (unit price per item)
- `total_purchase_price: 32400.0` (162.0 × 200, total for 200 items)

This follows standard e-commerce practice of displaying both unit and total prices for transparency.

#### Overhead Impact

Overhead percentage is applied to purchase price to calculate `calculated_purchase_price`:

```
calculated_purchase_price = purchase_price × (1 + overhead_percent / 100)
```

**Example:** Purchase price = 626.0, overhead = 10%

- `calculated_purchase_price` = 626.0 × 1.10 = 688.6
- If `sale_price` = 894.0 (list price), then `markup_pct` = (894.0 / 688.6 - 1) × 100 = 29.83

**Note:** Overhead only affects `calculated_purchase_price` and `markup_pct`. It does not change `list_price` or `purchase_price` values.

For detailed CLI logic and decision flow diagram, see [CLI Logic Documentation](docs/cli_main_py/cli_logic.md) (Mermaid diagram, also available as [SVG](docs/cli_main_py/cli_logic_chart.svg)).

## Tools

### Mermaid Diagram Extractor

The `tools/extract_mmd.py` module extracts Mermaid diagram blocks from Markdown files and saves them as `.mmd` files. If multiple Mermaid blocks are found, extracts all of them to separate numbered files (e.g., `output.mmd`, `output-2.mmd`, `output-3.mmd`). Optionally, it can automatically convert to SVG.

**Usage:**
```bash
# Extract mermaid diagram(s) (MMD will be generated in the same folder)
python -m tools.extract_mmd file.md

# Extract with explicit output path (if multiple blocks, uses numbered suffixes)
python -m tools.extract_mmd file.md --mmd output.mmd

# Extract and automatically convert to SVG (all blocks if multiple found)
python -m tools.extract_mmd file.md --svg output.svg

# Extract and convert to SVG with custom background
python -m tools.extract_mmd file.md --svg output.svg --background white
```

**Requirements:**

- None for extracting to MMD format (pure Python, uses standard library only)
- Mermaid CLI (mmdc) if `--svg` option is used: Install with `npm install -g @mermaid-js/mermaid-cli`

### Mermaid Block to SVG Image Replacer

The `tools/html_mmd2svg.py` module post-processes HTML files to replace Mermaid diagram code blocks with `<img>` tags pointing to corresponding SVG files. This is useful after converting Markdown to HTML to display rendered diagrams instead of code blocks.

**Usage:**
```bash
# Process HTML file (auto-detects SVG: {filename}_chart.svg or {filename}.svg)
python -m tools.html_mmd2svg file.html

# Process with explicit SVG path
python -m tools.html_mmd2svg file.html --svg diagram.svg
```

**Requirements:**

- None (pure Python, uses standard library only)

**Example workflow:**
```bash
# 1. Extract Mermaid diagram from Markdown
python -m tools.extract_mmd docs/cli_main_py/cli_logic.md --svg docs/cli_main_py/cli_logic_chart.svg

# 2. Convert Markdown to HTML
python -m tools.md2html docs/cli_main_py/cli_logic.md

# 3. Replace Mermaid code block with SVG image
python -m tools.html_mmd2svg docs/cli_main_py/cli_logic.html
```

### Markdown to HTML Converter

The `tools/md2html.py` module converts Markdown files to HTML with optional CSS style injection. It supports two conversion backends: pandoc (preferred) or node.js with marked library.

**Usage:**
```bash
# Convert a Markdown file (HTML will be generated in the same folder)
python -m tools.md2html file.md

# Convert with explicit output path
python -m tools.md2html file.md --html output.html

# Use specific converter
python -m tools.md2html file.md --converter pandoc
python -m tools.md2html file.md --converter node

# Add custom CSS style
python -m tools.md2html file.md --style custom.css
```

**Requirements:**

- pandoc (https://pandoc.org/installing.html) OR
- node.js (https://nodejs.org/) with npx (marked will be installed automatically)
- chardet (optional, recommended): For better encoding detection and warnings
  - Install with: `pip install chardet`
  - If not available, the module will use a simpler encoding check

### Mermaid Diagram to SVG Converter

The `tools/mmd2svg.py` module converts Mermaid diagram files (`.mmd`) to SVG format using Mermaid CLI.

**Usage:**
```bash
# Convert Mermaid diagram (SVG will be generated in the same folder)
python -m tools.mmd2svg file.mmd

# Convert with explicit output path
python -m tools.mmd2svg file.mmd --svg output.svg

# Specify background color
python -m tools.mmd2svg file.mmd --background transparent
```

**Requirements:**

- Mermaid CLI (mmdc): Install with `npm install -g @mermaid-js/mermaid-cli`

## Testing

Unit tests are available in the `untst/` folder, covering:

- datanorm_processor.py
- datanorm_parser.py
- main.py
- md2html.py
- extract_mmd.py
- mmd2svg.py
- html_mmd2svg.py

Run tests with:

```bash
python -m unittest discover untst -v
```

## License

Copyright (c) 2025 Daniil Korovinskiy
