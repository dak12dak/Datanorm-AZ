from __future__ import annotations

import csv
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import config

# Use slots=True for Python 3.10+ (memory optimization)
_dataclass_kwargs = {"slots": True} if sys.version_info >= (3, 10) else {}


@dataclass(**_dataclass_kwargs)
class Article:
    """Article master data coming from record type 'A'."""

    article_no  : str
    name        : str
    price_type  : Optional[int]
    price_value : Optional[float]
    unit        : Optional[str]
    raw_line    : str

    def list_price(self) -> Optional[float]:
        if self.price_type in (1, 9):
            return self.price_value
        return None

    def purchase_price(self) -> Optional[float]:
        if self.price_type == 2:
            return self.price_value
        return None


@dataclass(**_dataclass_kwargs)
class PriceStep:
    """Graduated price or discount coming from record type 'Z'."""

    article_no      : str
    step_code       : str
    description     : str
    price_kind      : Optional[int]
    sign            : Optional[str]
    base_price_type : Optional[int]
    value           : Optional[float]
    min_quantity    : Optional[float]
    max_quantity    : Optional[float]
    raw_line        : str


class DatanormProcessor:
    """
    Processor for DATANORM files.

    The processor streams the file, stores results in an in-memory SQLite database
    and offers helper methods for price calculations.
    """

    def __init__(self, database: str = ":memory:") -> None:
        self.conn = sqlite3.connect(database)
        self.conn.execute("PRAGMA journal_mode = OFF;")
        self.conn.execute("PRAGMA synchronous = OFF;")
        self._ensure_schema()

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def get_first_article_no(self) -> Optional[str]:
        """Get the first article number from the database, ordered by article_no."""
        row = self.conn.execute(
            "SELECT article_no FROM articles ORDER BY article_no LIMIT 1"
        ).fetchone()
        return row[0] if row else None

    def _ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                article_no      TEXT PRIMARY KEY,
                name            TEXT,
                unit            TEXT,
                list_price      REAL,
                purchase_price  REAL,
                raw_line        TEXT
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS price_steps (
                article_no       TEXT,
                step_code        TEXT,
                description      TEXT,
                price_kind       INTEGER,
                sign             TEXT,
                base_price_type  INTEGER,
                value            REAL,
                min_quantity     REAL,
                max_quantity     REAL,
                raw_line         TEXT,
                PRIMARY KEY (article_no, step_code)
            )
            """
        )

    @staticmethod
    def _parse_int(fields: List[str], index: int) -> Optional[int]:
        if len(fields) <= index:
            return None
        value = fields[index].strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_float(value: str) -> Optional[float]:
        if not value:
            return None
        value = value.replace(",", ".")
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _create_article(
        article_no  : str,
        name        : str,
        price_type  : Optional[int],
        price_value : Optional[float],
        unit        : Optional[str],
        raw_line    : str,
    ) -> Article:
        """Create an Article instance with given parameters."""
        return Article(
            article_no  = article_no,
            name        = name,
            price_type  = price_type,
            price_value = price_value,
            unit        = unit,
            raw_line    = raw_line,
        )

    @staticmethod
    def _parse_article(fields: List[str], raw_line: str) -> Article:
        price_type  = DatanormProcessor._parse_int(fields, 7)
        price_value = DatanormProcessor._parse_float(fields[8]) if len(fields) > 8 else None
        unit        = fields[5] if len(fields) > 5 and fields[5] else None
        name        = fields[3] if len(fields) > 3 else ""
        article_no  = fields[2]
        return DatanormProcessor._create_article(
            article_no, name, price_type, price_value, unit, raw_line
        )

    @staticmethod
    def _parse_price_step(fields: List[str], raw_line: str) -> PriceStep:
        price_kind      = DatanormProcessor._parse_int(fields, 7)
        sign            = fields[8] if len(fields) > 8 else None
        base_price_type = DatanormProcessor._parse_int(fields, 9)
        value           = DatanormProcessor._parse_float(fields[11]) if len(fields) > 11 else None
        min_quantity    = DatanormProcessor._parse_float(fields[14]) if len(fields) > 14 else None
        max_quantity    = DatanormProcessor._parse_float(fields[15]) if len(fields) > 15 else None

        return PriceStep(
            article_no      = fields[2],
            step_code       = fields[3],
            description     = fields[5],
            price_kind      = price_kind,
            sign            = sign,
            base_price_type = base_price_type,
            value           = value,
            min_quantity    = min_quantity,
            max_quantity    = max_quantity,
            raw_line        = raw_line,
        )

    def load_file(self, path: Path, encoding: Optional[str] = None) -> None:
        """
        Stream the DATANORM file into the in-memory database.
        Only record types 'A' (articles) and 'Z' (graduated prices) are persisted.
        """
        if encoding is None:
            encoding = config.default_input_encoding
        with path.open("r", encoding=encoding, errors="ignore") as handle:
            for line_no, raw_line in enumerate(handle, start=1):
                raw_line = raw_line.rstrip("\r\n")
                if not raw_line:
                    continue
                record_type = raw_line[0]
                fields = raw_line.split(";")
                try:
                    if record_type == "A":
                        article = self._parse_article(fields, raw_line)
                        self._upsert_article(article)
                    elif record_type == "Z":
                        price_step = self._parse_price_step(fields, raw_line)
                        self._upsert_price_step(price_step)
                except (ValueError, IndexError, KeyError) as exc:
                    # Specific exceptions for parsing errors (missing fields, invalid values, etc.)
                    raise ValueError(f"Error parsing line {line_no}: {exc}\n{raw_line}") from exc
                except Exception as exc:  # pragma: no cover - defensive
                    # Catch-all for unexpected errors (database errors, etc.)
                    raise ValueError(f"Unexpected error parsing line {line_no}: {exc}\n{raw_line}") from exc
        self.conn.commit()

    def _upsert_article(self, article: Article) -> None:
        """Insert or update article: update value if new value is not None, otherwise keep old value."""
        existing = self.conn.execute(
            """
            SELECT
                list_price,
                purchase_price,
                name,
                unit
              FROM articles
             WHERE article_no = ?
            """,
            (article.article_no,),
        ).fetchone()

        list_price     = article.list_price()
        purchase_price = article.purchase_price()

        if existing:
            current_list, current_purchase, current_name, current_unit = existing
            if list_price is None:
                list_price = current_list
            if purchase_price is None:
                purchase_price = current_purchase
            if not article.name:
                article = DatanormProcessor._create_article(
                    article_no  = article.article_no,
                    name        = current_name or "",
                    price_type  = article.price_type,
                    price_value = article.price_value,
                    unit        = article.unit or current_unit,
                    raw_line    = article.raw_line,
                )

        self.conn.execute(
            """
            INSERT INTO articles (
                article_no,
                name,
                unit,
                list_price,
                purchase_price,
                raw_line
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(article_no) DO UPDATE SET
                name           = excluded.name,
                unit           = COALESCE(excluded.unit, articles.unit),
                list_price     = COALESCE(excluded.list_price, articles.list_price),
                purchase_price = COALESCE(excluded.purchase_price, articles.purchase_price),
                raw_line       = excluded.raw_line
            """,
            (
                article.article_no,
                article.name,
                article.unit,
                list_price,
                purchase_price,
                article.raw_line,
            ),
        )

    def _upsert_price_step(self, step: PriceStep) -> None:
        """Insert or update price step, overwriting only provided fields."""
        self.conn.execute(
            """
            INSERT INTO price_steps (
                article_no,
                step_code,
                description,
                price_kind,
                sign,
                base_price_type,
                value,
                min_quantity,
                max_quantity,
                raw_line
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(article_no, step_code) DO UPDATE SET
                description     = excluded.description,
                price_kind      = excluded.price_kind,
                sign            = excluded.sign,
                base_price_type = excluded.base_price_type,
                value           = excluded.value,
                min_quantity    = excluded.min_quantity,
                max_quantity    = excluded.max_quantity,
                raw_line        = excluded.raw_line
            """,
            (
                step.article_no,
                step.step_code,
                step.description,
                step.price_kind,
                step.sign,
                step.base_price_type,
                step.value,
                step.min_quantity,
                step.max_quantity,
                step.raw_line,
            ),
        )

    def lookup_article(self, article_no: str) -> Optional[Dict[str, object]]:
        row = self.conn.execute(
            """
            SELECT
                article_no,
                name,
                unit,
                list_price,
                purchase_price
              FROM articles
             WHERE article_no = ?
            """,
            (article_no,),
        ).fetchone()
        if not row:
            return None
        steps = self.conn.execute(
            """
            SELECT
                step_code,
                description,
                price_kind,
                sign,
                base_price_type,
                value,
                min_quantity,
                max_quantity
              FROM price_steps
             WHERE article_no = ?
             ORDER BY min_quantity ASC
            """,
            (article_no,),
        ).fetchall()
        return {
            "article_no"         : row[0],
            "name"               : row[1],
            "unit"               : row[2],
            "list_price"         : row[3],
            "purchase_price"     : row[4],
            "availability_status": "Article found, stock level unknown",
            "price_steps"        : [
                {
                    "step_code"      : step[0],
                    "description"    : step[1],
                    "price_kind"     : step[2],
                    "sign"           : step[3],
                    "base_price_type": step[4],
                    "value"          : step[5],
                    "min_quantity"   : step[6],
                    "max_quantity"   : step[7],
                }
                for step in steps
            ],
        }

    def calculate_prices(
        self,
        overhead_percent : float = 0.0,
        limit            : Optional[int] = None,
        article_no       : Optional[str] = None,
        quantity         : Optional[float] = None,
    ) -> List[Dict[str, object]]:
        """
        Calculate derived price information for all articles.

        The algorithm uses the following heuristics:
        - List price: direct list price from article record (price_type 1 or 9)
          or the lowest graduated price with base_price_type=1.
        - Purchase price: from the article record (price_type 2) or the lowest
          graduated price with base_price_type=2.
        - Supplier discount (percent): relative difference between list and purchase.
        - Overhead percent: fixed input parameter applied on top of purchase price.
        - Calculated purchase price: purchase_price * (1 + overhead_percent / 100).
        - Sale price: list price if available, otherwise calculated purchase price.
        - Markup percent: relative difference between sale price and calculated purchase price.
        """
        def round_price(value: float, digits: Optional[int] = None) -> float:
            """Round price value to specified number of decimal digits.
            
            Args:
                value: Value to round
                digits: Number of decimal digits (must be >= 0, will be converted to int).
                       If None, uses config.ROUND_TO_DEC_DIGIT, or 0 if config is also None
                
            Returns:
                Rounded value
                
            Raises:
                ValueError: If digits is negative or cannot be converted to int
            """
            if digits is None:
                digits = config.ROUND_TO_DEC_DIGIT if config.ROUND_TO_DEC_DIGIT is not None else 0
            try:
                digits = int(digits)
            except (TypeError, ValueError):
                raise ValueError(f"digits must be an integer, got: {type(digits).__name__}")
            if digits < 0:
                raise ValueError(f"digits must be >= 0, got: {digits}")
            return round(value, digits)
        
        cursor = self.conn.cursor()
        if article_no:
            cursor.execute(
                """
                SELECT
                    article_no,
                    name,
                    unit,
                    list_price,
                    purchase_price
                  FROM articles
                 WHERE article_no = ?
                 ORDER BY article_no
                """,
                (article_no,),
            )
        else:
            cursor.execute(
                """
                SELECT
                    article_no,
                    name,
                    unit,
                    list_price,
                    purchase_price
                  FROM articles
                 ORDER BY article_no
                """
            )
        articles = cursor.fetchall()

        if limit is not None:
            articles = articles[:limit]

        price_steps_map: Dict[str, List[Tuple]] = {}
        placeholders = ",".join("?" for _ in articles) if articles else ""
        if placeholders:
            cursor.execute(
                f"""
                SELECT
                    article_no,
                    price_kind,
                    sign,
                    base_price_type,
                    value,
                    min_quantity,
                    max_quantity
                  FROM price_steps
                 WHERE article_no IN ({placeholders})
                 ORDER BY article_no, min_quantity
                """,
                [row[0] for row in articles],
            )
            for step in cursor.fetchall():
                price_steps_map.setdefault(step[0], []).append(step[1:])

        results: List[Dict[str, object]] = []
        for art_no, name, unit, list_price, purchase_price in articles:
            steps = price_steps_map.get(art_no, [])
            
            # Get base prices (for discount calculation)
            # Note: If price exists both in article record (A) and price steps (Z),
            # the priority is: price from steps for specified quantity > price from A > first step.
            # This handles cases where both sources have prices (data inconsistency).
            base_list_price     = list_price if list_price is not None else self._first_price_from_steps(steps, base_price_type=1)
            base_purchase_price = purchase_price if purchase_price is not None else self._first_price_from_steps(steps, base_price_type=2)
            
            # Get quantity-specific prices (default to quantity=1 if not specified)
            qty = quantity if quantity is not None else 1.0
            qty_list_price     = self._price_from_steps_by_quantity(steps, base_price_type=1, quantity=qty)
            qty_purchase_price = self._price_from_steps_by_quantity(steps, base_price_type=2, quantity=qty)
            list_price        = qty_list_price if qty_list_price is not None else base_list_price
            purchase_price    = qty_purchase_price if qty_purchase_price is not None else base_purchase_price
            
            supplier_discount_pct = None
            if list_price and purchase_price and list_price > 0:
                supplier_discount_pct = round_price((1.0 - purchase_price / list_price) * 100.0)

            calculated_purchase = None
            if purchase_price is not None:
                calculated_purchase = round_price(purchase_price * (1.0 + overhead_percent / 100.0))

            sale_price = list_price if list_price is not None else calculated_purchase
            markup_pct = None
            if sale_price is not None and calculated_purchase is not None:
                if calculated_purchase != 0:
                    markup_pct = round_price((sale_price / calculated_purchase - 1.0) * 100.0)

            # Calculate total prices if quantity is specified
            total_list_price = None
            total_purchase_price = None
            total_calculated_purchase_price = None
            total_sale_price = None
            if quantity is not None and quantity > 0:
                if list_price is not None:
                    total_list_price = round_price(list_price * quantity)
                if purchase_price is not None:
                    total_purchase_price = round_price(purchase_price * quantity)
                if calculated_purchase is not None:
                    total_calculated_purchase_price = round_price(calculated_purchase * quantity)
                if sale_price is not None:
                    total_sale_price = round_price(sale_price * quantity)

            result = {
                "article_no"               : art_no,
                "name"                     : name,
                "unit"                     : unit,
                "list_price"               : list_price,
                "supplier_discount_pct"    : supplier_discount_pct,
                "purchase_price"           : purchase_price,
                "overhead_pct"             : overhead_percent,
                "calculated_purchase_price": calculated_purchase,
                "markup_pct"               : markup_pct,
                "sale_price"               : sale_price,
            }
            
            # Add total prices if quantity is specified
            if quantity is not None and quantity > 0:
                result["quantity"] = quantity
                result["total_list_price"] = total_list_price
                result["total_purchase_price"] = total_purchase_price
                result["total_calculated_purchase_price"] = total_calculated_purchase_price
                result["total_sale_price"] = total_sale_price
            
            results.append(result)
        return results

    @staticmethod
    def _first_price_from_steps(steps: List[Tuple], base_price_type: int) -> Optional[float]:
        for price_kind, sign, base_type, value, min_qty, max_qty in steps:
            if base_type == base_price_type and price_kind == 1:
                return value
        return None

    @staticmethod
    def _price_from_steps_by_quantity(
        steps: List[Tuple], base_price_type: int, quantity: float
    ) -> Optional[float]:
        """Find price from steps that matches the given quantity range."""
        for price_kind, sign, base_type, value, min_qty, max_qty in steps:
            if base_type == base_price_type and price_kind == 1:
                min_q = min_qty if min_qty is not None else 0.0
                max_q = max_qty if max_qty is not None else float("inf")
                if min_q <= quantity <= max_q:
                    return value
        return None

    def export_prices_to_csv(
        self,
        output_path     : Path,
        overhead_percent: float = 0.0,
        article_no      : Optional[str] = None,
        limit           : Optional[int] = None,
        quantity        : Optional[float] = None,
        encoding        : Optional[str] = None,
    ) -> None:
        data = self.calculate_prices(
            overhead_percent = overhead_percent,
            article_no       = article_no,
            limit            = limit,
            quantity         = quantity,
        )
        # Determine fieldnames based on whether quantity is specified
        fieldnames = [
            "article_no",
            "name",
            "unit",
            "list_price",
            "supplier_discount_pct",
            "purchase_price",
            "overhead_pct",
            "calculated_purchase_price",
            "markup_pct",
            "sale_price",
        ]
        
        # Add quantity and total price fields if quantity is specified
        if quantity is not None and quantity > 0:
            fieldnames.extend([
                "quantity",
                "total_list_price",
                "total_purchase_price",
                "total_calculated_purchase_price",
                "total_sale_price",
            ])
        if encoding is None:
            encoding = config.default_output_encoding
        with output_path.open("w", encoding=encoding, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)


def fetch_prices(
    file_path: Path,
    overhead_percent: float = 0.0,
) -> Tuple[DatanormProcessor, List[Dict[str, object]]]:
    processor = DatanormProcessor()
    processor.load_file(file_path)
    results = processor.calculate_prices(overhead_percent=overhead_percent)
    return processor, results
