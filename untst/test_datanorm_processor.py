"""Tests for datanorm_processor module.

Test Coverage:

Tested:

Article methods:
- Article.list_price() - price_type 1, 9, and other types
- Article.purchase_price() - price_type 2 and other types

Parsing methods:
- _parse_int() - valid, empty, missing index, invalid values
- _parse_float() - dot/comma separators, empty, invalid values
- _parse_article() - creates Article from fields
- _parse_price_step() - creates PriceStep from fields

Database operations:
- DatanormProcessor.__init__() - initialization with in-memory database
- _ensure_schema() - database schema creation
- get_first_article_no() - returns first article number, None if no articles
- close() - closes database connection
- _upsert_article() - insert new article, update preserving existing values,
  empty name preserves existing name
- _upsert_price_step() - insert price step, update existing step

File operations:
- load_file() - basic file loading, nonexistent file, invalid data,
  ignores other record types, empty lines,
  different encodings (UTF-8, Windows-1251)

Query operations:
- lookup_article() - found/not found, with price steps

Price calculation:
- calculate_prices() - simple prices, with overhead, discounts,
  quantity-based pricing, limit, specific article,
  edge cases: no articles, list_price=0, calculated_purchase=0,
  multiple steps with same base_price_type,
  total prices calculation when quantity is specified
- round_price() - rounding function for prices and percentages
- _first_price_from_steps() - finds first matching price
- _price_from_steps_by_quantity() - finds price by quantity range

Export operations:
- export_prices_to_csv() - creates CSV file,
  article_no with limit combination, different encodings (UTF-8)

Convenience functions:
- fetch_prices() - convenience function

Not Tested:
- _create_article() - used internally, not tested directly
"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datanorm_processor import (
    Article,
    DatanormProcessor,
    PriceStep,
    fetch_prices,
)


class TestArticle(unittest.TestCase):
    """Test Article dataclass methods."""

    def test_list_price_type_1(self):
        """Test list_price returns value for price_type 1."""
        article = Article(
            article_no  = "TEST",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;...",
        )
        self.assertEqual(article.list_price(), 100.0)

    def test_list_price_type_9(self):
        """Test list_price returns value for price_type 9."""
        article = Article(
            article_no  = "TEST",
            name        = "Test Article",
            price_type  = 9,
            price_value = 200.0,
            unit        = "PCS",
            raw_line    = "A;...",
        )
        self.assertEqual(article.list_price(), 200.0)

    def test_list_price_other_type(self):
        """Test list_price returns None for other price types."""
        article = Article(
            article_no  = "TEST",
            name        = "Test Article",
            price_type  = 2,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;...",
        )
        self.assertIsNone(article.list_price())

    def test_purchase_price_type_2(self):
        """Test purchase_price returns value for price_type 2."""
        article = Article(
            article_no  = "TEST",
            name        = "Test Article",
            price_type  = 2,
            price_value = 80.0,
            unit        = "PCS",
            raw_line    = "A;...",
        )
        self.assertEqual(article.purchase_price(), 80.0)

    def test_purchase_price_other_type(self):
        """Test purchase_price returns None for other price types."""
        article = Article(
            article_no  = "TEST",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;...",
        )
        self.assertIsNone(article.purchase_price())


class TestParsingMethods(unittest.TestCase):
    """Test static parsing methods."""

    def test_parse_int_valid(self):
        """Test _parse_int with valid integer."""
        fields = ["", "", "", "", "", "", "", "123"]
        result = DatanormProcessor._parse_int(fields, 7)
        self.assertEqual(result, 123)

    def test_parse_int_empty(self):
        """Test _parse_int with empty field."""
        fields = ["", "", "", "", "", "", "", ""]
        result = DatanormProcessor._parse_int(fields, 7)
        self.assertIsNone(result)

    def test_parse_int_missing_index(self):
        """Test _parse_int with missing index."""
        fields = ["", "", ""]
        result = DatanormProcessor._parse_int(fields, 7)
        self.assertIsNone(result)

    def test_parse_int_invalid(self):
        """Test _parse_int with invalid value."""
        fields = ["", "", "", "", "", "", "", "abc"]
        result = DatanormProcessor._parse_int(fields, 7)
        self.assertIsNone(result)

    def test_parse_float_valid_dot(self):
        """Test _parse_float with dot separator."""
        result = DatanormProcessor._parse_float("123.45")
        self.assertEqual(result, 123.45)

    def test_parse_float_valid_comma(self):
        """Test _parse_float with comma separator."""
        result = DatanormProcessor._parse_float("123,45")
        self.assertEqual(result, 123.45)

    def test_parse_float_empty(self):
        """Test _parse_float with empty string."""
        result = DatanormProcessor._parse_float("")
        self.assertIsNone(result)

    def test_parse_float_invalid(self):
        """Test _parse_float with invalid value."""
        result = DatanormProcessor._parse_float("abc")
        self.assertIsNone(result)

    def test_parse_article(self):
        """Test _parse_article creates Article correctly."""
        fields = ["A", "N", "ART001", "Test Article", "", "PCS", "1", "1", "100.0"]
        raw_line = "A;N;ART001;Test Article;;PCS;1;1;100.0"
        article = DatanormProcessor._parse_article(fields, raw_line)
        self.assertEqual(article.article_no, "ART001")
        self.assertEqual(article.name, "Test Article")
        self.assertEqual(article.price_type, 1)
        self.assertEqual(article.price_value, 100.0)
        self.assertEqual(article.unit, "PCS")

    def test_parse_price_step(self):
        """Test _parse_price_step creates PriceStep correctly."""
        fields = [
            "Z",
            "N",
            "ART002",
            "02",
            "2",
            "Bulk discount",
            "Extended description",
            "1",
            "-",
            "2",
            "3",
            "85.5",
            "",
            "4",
            "5.0",
            "25.0",
        ]
        raw_line = "Z;N;ART002;02;2;Bulk discount;Extended description;1;-;2;3;85.5;;4;5.0;25.0"
        step = DatanormProcessor._parse_price_step(fields, raw_line)
        self.assertEqual(step.article_no, "ART002")
        self.assertEqual(step.step_code, "02")
        self.assertEqual(step.description, "Bulk discount")
        self.assertEqual(step.price_kind, 1)
        self.assertEqual(step.sign, "-")
        self.assertEqual(step.base_price_type, 2)
        self.assertEqual(step.value, 85.5)
        self.assertEqual(step.min_quantity, 5.0)
        self.assertEqual(step.max_quantity, 25.0)


class TestDatanormProcessor(unittest.TestCase):
    """Test DatanormProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = DatanormProcessor()

    def test_initialization(self):
        """Test processor initializes with in-memory database."""
        processor = DatanormProcessor()
        self.assertIsNotNone(processor.conn)

    def test_schema_creation(self):
        """Test database schema is created."""
        cursor = self.processor.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='articles'"
        )
        self.assertIsNotNone(cursor.fetchone())
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='price_steps'"
        )
        self.assertIsNotNone(cursor.fetchone())

    def test_get_first_article_no_with_articles(self):
        """Test get_first_article_no returns first article when articles exist."""
        # Add test articles
        with tempfile.NamedTemporaryFile(mode="w", suffix=".001", delete=False) as f:
            f.write("A;N;ART002;Article 2;;PCS;1;1;200.0\n")
            f.write("A;N;ART001;Article 1;;PCS;1;1;100.0\n")
            f.write("A;N;ART003;Article 3;;PCS;1;1;300.0\n")
            temp_path = Path(f.name)

        try:
            self.processor.load_file(temp_path)
            # Should return first article ordered by article_no
            first_article = self.processor.get_first_article_no()
            self.assertEqual(first_article, "ART001")
        finally:
            temp_path.unlink()

    def test_get_first_article_no_no_articles(self):
        """Test get_first_article_no returns None when no articles exist."""
        first_article = self.processor.get_first_article_no()
        self.assertIsNone(first_article)

    def test_close(self):
        """Test close method closes the database connection."""
        processor = DatanormProcessor()
        self.assertIsNotNone(processor.conn)
        processor.close()
        # After closing, connection should be closed
        with self.assertRaises(sqlite3.ProgrammingError):
            processor.conn.execute("SELECT 1")

    def test_load_file_simple(self):
        """Test loading a simple DATANORM file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".001", delete=False) as f:
            f.write("A;N;ART001;Test Article;;PCS;1;1;100.0\n")
            f.write("Z;N;ART001;01;1;Step 1;Step 1;1;+;1;1;90.0;;1;1.0;10.0\n")
            temp_path = Path(f.name)

        try:
            self.processor.load_file(temp_path)
            article = self.processor.lookup_article("ART001")
            self.assertIsNotNone(article)
            assert article is not None  # Type narrowing
            self.assertEqual(article["article_no"], "ART001")
            self.assertEqual(article["name"], "Test Article")
        finally:
            temp_path.unlink()

    def test_load_file_nonexistent(self):
        """Test load_file raises FileNotFoundError for nonexistent file."""
        nonexistent = Path("nonexistent_file.001")
        with self.assertRaises(FileNotFoundError):
            self.processor.load_file(nonexistent)

    def test_load_file_invalid_data(self):
        """Test load_file raises ValueError for invalid data."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".001", delete=False) as f:
            f.write("A;N\n")  # Incomplete record - missing article_no (fields[2])
            temp_path = Path(f.name)

        try:
            with self.assertRaises(ValueError) as context:
                self.processor.load_file(temp_path)
            self.assertIn("Error parsing line", str(context.exception))
        finally:
            temp_path.unlink()

    def test_load_file_ignores_other_record_types(self):
        """Test load_file ignores record types other than A and Z."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".001", delete=False) as f:
            f.write("A;N;ART001;Test Article;;PCS;1;1;100.0\n")
            f.write("V;N;Some other record\n")  # Record type V - should be ignored
            f.write("E;N;Another record\n")  # Record type E - should be ignored
            f.write("Z;N;ART001;01;1;Step 1;Step 1;1;+;1;1;90.0;;1;1.0;10.0\n")
            temp_path = Path(f.name)

        try:
            self.processor.load_file(temp_path)
            # Should only have ART001, not the V and E records
            article = self.processor.lookup_article("ART001")
            self.assertIsNotNone(article)
            assert article is not None  # Type narrowing
            self.assertEqual(article["article_no"], "ART001")
        finally:
            temp_path.unlink()

    def test_load_file_empty_lines(self):
        """Test load_file handles empty lines correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".001", delete=False) as f:
            f.write("\n")  # Empty line
            f.write("A;N;ART001;Test Article;;PCS;1;1;100.0\n")
            f.write("\n")  # Another empty line
            f.write("Z;N;ART001;01;1;Step 1;Step 1;1;+;1;1;90.0;;1;1.0;10.0\n")
            temp_path = Path(f.name)

        try:
            self.processor.load_file(temp_path)
            article = self.processor.lookup_article("ART001")
            self.assertIsNotNone(article)
            assert article is not None  # Type narrowing
            self.assertEqual(article["article_no"], "ART001")
        finally:
            temp_path.unlink()

    def test_upsert_article_insert(self):
        """Test inserting new article."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)
        result = self.processor.conn.execute(
            "SELECT article_no, name, list_price FROM articles WHERE article_no = ?",
            ("ART001",),
        ).fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "ART001")
        self.assertEqual(result[1], "Test Article")
        self.assertEqual(result[2], 100.0)

    def test_upsert_article_update_preserves_existing(self):
        """Test updating article preserves existing values when new values are None."""
        # Insert article with list_price
        article1 = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article1)

        # Update with None prices - should preserve existing
        article2 = Article(
            article_no  = "ART001",
            name        = "Updated Name",
            price_type  = None,
            price_value = None,
            unit        = "KG",
            raw_line    = "A;N;ART001;Updated Name;;KG;;;",
        )
        self.processor._upsert_article(article2)

        result = self.processor.conn.execute(
            "SELECT name, list_price FROM articles WHERE article_no = ?",
            ("ART001",),
        ).fetchone()
        self.assertEqual(result[0], "Updated Name")
        self.assertEqual(result[1], 100.0)  # Preserved

    def test_upsert_article_empty_name_preserves_existing(self):
        """Test updating article with empty name preserves existing name."""
        # Insert article with name
        article1 = Article(
            article_no  = "ART001",
            name        = "Original Name",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Original Name;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article1)

        # Update with empty name - should preserve existing name
        article2 = Article(
            article_no  = "ART001",
            name        = "",  # Empty name
            price_type  = 2,
            price_value = 80.0,
            unit        = "KG",
            raw_line    = "A;N;ART001;;;KG;;2;80.0",
        )
        self.processor._upsert_article(article2)

        result = self.processor.conn.execute(
            "SELECT name, purchase_price FROM articles WHERE article_no = ?",
            ("ART001",),
        ).fetchone()
        self.assertEqual(result[0], "Original Name")  # Preserved from existing
        self.assertEqual(result[1], 80.0)  # Updated

    def test_upsert_price_step(self):
        """Test inserting price step."""
        step = PriceStep(
            article_no      = "ART001",
            step_code       = "01",
            description     = "Step 1",
            price_kind      = 1,
            sign            = "+",
            base_price_type = 1,
            value           = 100.0,
            min_quantity    = 1.0,
            max_quantity    = 10.0,
            raw_line        = "Z;N;ART001;01;1;Step 1;Step 1;1;+;1;1;100.0;;1;1.0;10.0",
        )
        self.processor._upsert_price_step(step)
        result = self.processor.conn.execute(
            "SELECT article_no, step_code, value FROM price_steps WHERE article_no = ?",
            ("ART001",),
        ).fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "ART001")
        self.assertEqual(result[1], "01")
        self.assertEqual(result[2], 100.0)

    def test_upsert_price_step_update_existing(self):
        """Test updating existing price step."""
        # Insert initial price step
        step1 = PriceStep(
            article_no      = "ART001",
            step_code       = "01",
            description     = "Step 1",
            price_kind      = 1,
            sign            = "+",
            base_price_type = 1,
            value           = 100.0,
            min_quantity    = 1.0,
            max_quantity    = 10.0,
            raw_line        = "Z;N;ART001;01;1;Step 1;Step 1;1;+;1;1;100.0;;1;1.0;10.0",
        )
        self.processor._upsert_price_step(step1)

        # Update with same article_no and step_code but different values
        step2 = PriceStep(
            article_no      = "ART001",
            step_code       = "01",  # Same step_code - should update
            description     = "Updated Step",
            price_kind      = 1,
            sign            = "-",
            base_price_type = 2,
            value           = 200.0,
            min_quantity    = 5.0,
            max_quantity    = 20.0,
            raw_line        = "Z;N;ART001;01;1;Updated Step;Updated Step;1;-;2;1;200.0;;1;5.0;20.0",
        )
        self.processor._upsert_price_step(step2)

        result = self.processor.conn.execute(
            "SELECT description, sign, base_price_type, value, min_quantity, max_quantity FROM price_steps WHERE article_no = ? AND step_code = ?",
            ("ART001", "01"),
        ).fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "Updated Step")  # Updated
        self.assertEqual(result[1], "-")  # Updated
        self.assertEqual(result[2], 2)  # Updated
        self.assertEqual(result[3], 200.0)  # Updated
        self.assertEqual(result[4], 5.0)  # Updated
        self.assertEqual(result[5], 20.0)  # Updated

        # Should still have only one record (not duplicate)
        count = self.processor.conn.execute(
            "SELECT COUNT(*) FROM price_steps WHERE article_no = ? AND step_code = ?",
            ("ART001", "01"),
        ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_lookup_article_not_found(self):
        """Test lookup_article returns None for non-existent article."""
        result = self.processor.lookup_article("NONEXISTENT")
        self.assertIsNone(result)

    def test_lookup_article_with_steps(self):
        """Test lookup_article returns article with price steps."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)

        step = PriceStep(
            article_no      = "ART001",
            step_code       = "01",
            description     = "Step 1",
            price_kind      = 1,
            sign            = "+",
            base_price_type = 1,
            value           = 90.0,
            min_quantity    = 1.0,
            max_quantity    = 10.0,
            raw_line        = "Z;N;ART001;01;1;Step 1;Step 1;1;+;1;1;90.0;;1;1.0;10.0",
        )
        self.processor._upsert_price_step(step)

        result = self.processor.lookup_article("ART001")
        self.assertIsNotNone(result)
        assert result is not None  # Type narrowing
        self.assertEqual(result["article_no"], "ART001")
        price_steps = result["price_steps"]
        assert isinstance(price_steps, list)  # Type narrowing
        self.assertEqual(len(price_steps), 1)
        self.assertEqual(price_steps[0]["step_code"], "01")

    def test_calculate_prices_simple(self):
        """Test calculate_prices with simple article."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)

        prices = self.processor.calculate_prices()
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["article_no"], "ART001")
        self.assertEqual(prices[0]["list_price"], 100.0)
        self.assertEqual(prices[0]["sale_price"], 100.0)

    def test_calculate_prices_with_overhead(self):
        """Test calculate_prices with overhead."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 2,
            price_value = 80.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;2;1;80.0",
        )
        self.processor._upsert_article(article)

        prices = self.processor.calculate_prices(overhead_percent=10.0)
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["purchase_price"], 80.0)
        self.assertEqual(prices[0]["calculated_purchase_price"], 88.0)  # 80 * 1.1
        self.assertEqual(prices[0]["sale_price"], 88.0)

    def test_calculate_prices_with_discount(self):
        """Test calculate_prices calculates supplier discount."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)

        # Add purchase price via second record
        article2 = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 2,
            price_value = 80.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;2;1;80.0",
        )
        self.processor._upsert_article(article2)

        prices = self.processor.calculate_prices()
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["list_price"], 100.0)
        self.assertEqual(prices[0]["purchase_price"], 80.0)
        discount = prices[0]["supplier_discount_pct"]
        self.assertIsNotNone(discount)
        assert discount is not None and isinstance(discount, (int, float))  # Type narrowing
        self.assertEqual(float(discount), 20.0)  # (1 - 80/100) * 100, rounded to 2 decimals

    def test_calculate_prices_with_quantity(self):
        """Test calculate_prices with quantity-based pricing."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)

        # Add quantity-based price step
        step = PriceStep(
            article_no      = "ART001",
            step_code       = "01",
            description     = "Bulk discount",
            price_kind      = 1,
            sign            = "+",
            base_price_type = 1,
            value           = 90.0,
            min_quantity    = 10.0,
            max_quantity    = 100.0,
            raw_line        = "Z;N;ART001;01;1;Bulk discount;Bulk discount;1;+;1;1;90.0;;1;10.0;100.0",
        )
        self.processor._upsert_price_step(step)

        # Test with quantity in range
        prices = self.processor.calculate_prices(quantity=50.0)
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["list_price"], 90.0)  # From step
        # Check total prices are calculated
        self.assertEqual(prices[0]["quantity"], 50.0)
        self.assertEqual(prices[0]["total_list_price"], 4500.0)  # 90.0 * 50

        # Test with quantity outside range
        prices = self.processor.calculate_prices(quantity=5.0)
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["list_price"], 100.0)  # From article
        # Check total prices are calculated
        self.assertEqual(prices[0]["quantity"], 5.0)
        self.assertEqual(prices[0]["total_list_price"], 500.0)  # 100.0 * 5
        
        # Test without quantity - total prices should not be present
        prices = self.processor.calculate_prices()
        self.assertEqual(len(prices), 1)
        self.assertNotIn("quantity", prices[0])
        self.assertNotIn("total_list_price", prices[0])

    def test_calculate_prices_total_prices(self):
        """Test calculate_prices calculates total prices when quantity is specified."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)

        # Add purchase price
        article2 = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 2,
            price_value = 80.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;2;1;80.0",
        )
        self.processor._upsert_article(article2)

        # Test with quantity
        prices = self.processor.calculate_prices(quantity=200.0, overhead_percent=10.0)
        self.assertEqual(len(prices), 1)
        
        # Check unit prices
        self.assertEqual(prices[0]["list_price"], 100.0)
        self.assertEqual(prices[0]["purchase_price"], 80.0)
        self.assertEqual(prices[0]["calculated_purchase_price"], 88.0)  # 80 * 1.1
        self.assertEqual(prices[0]["sale_price"], 100.0)
        
        # Check total prices
        self.assertEqual(prices[0]["quantity"], 200.0)
        self.assertEqual(prices[0]["total_list_price"], 20000.0)  # 100.0 * 200
        self.assertEqual(prices[0]["total_purchase_price"], 16000.0)  # 80.0 * 200
        self.assertEqual(prices[0]["total_calculated_purchase_price"], 17600.0)  # 88.0 * 200
        self.assertEqual(prices[0]["total_sale_price"], 20000.0)  # 100.0 * 200
        
        # Test without quantity - total prices should not be present
        prices = self.processor.calculate_prices(overhead_percent=10.0)
        self.assertEqual(len(prices), 1)
        self.assertNotIn("quantity", prices[0])
        self.assertNotIn("total_list_price", prices[0])
        self.assertNotIn("total_purchase_price", prices[0])

    def test_calculate_prices_rounding(self):
        """Test calculate_prices rounds calculated values to 2 decimal places."""
        # Test with values that produce long decimal results
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 894.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;894.0",
        )
        self.processor._upsert_article(article)

        # Add purchase price
        article2 = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 2,
            price_value = 626.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;2;1;626.0",
        )
        self.processor._upsert_article(article2)

        prices = self.processor.calculate_prices()
        self.assertEqual(len(prices), 1)
        
        # supplier_discount_pct = (1 - 626/894) * 100 = 29.977628635346754 -> should round to 29.98
        self.assertEqual(prices[0]["supplier_discount_pct"], 29.98)
        
        # Test with overhead
        prices = self.processor.calculate_prices(overhead_percent=10.0)
        # calculated_purchase_price = 626.0 * 1.10 = 688.6
        self.assertEqual(prices[0]["calculated_purchase_price"], 688.6)
        # markup_pct = (894.0 / 688.6 - 1) * 100 = 29.82863781585825 -> should round to 29.83
        self.assertEqual(prices[0]["markup_pct"], 29.83)

    def test_round_price_invalid_digits(self):
        """Test round_price function handles invalid digits parameter."""
        # Add article with both list and purchase price to ensure round_price is called
        article1 = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article1)
        
        article2 = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 2,
            price_value = 80.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;2;1;80.0",
        )
        self.processor._upsert_article(article2)
        
        # Test with negative digits - should raise ValueError
        # We need to patch config.ROUND_TO_DEC_DIGIT to test this
        import config
        original_value = config.ROUND_TO_DEC_DIGIT
        
        try:
            # Test with negative value
            config.ROUND_TO_DEC_DIGIT = -1
            with self.assertRaises(ValueError) as context:
                self.processor.calculate_prices()
            self.assertIn("digits must be >= 0", str(context.exception))
            
            # Test with None - should default to 0
            config.ROUND_TO_DEC_DIGIT = None
            prices = self.processor.calculate_prices()
            # Should work, using 0 as default (rounds to integer)
            self.assertEqual(len(prices), 1)
            self.assertEqual(prices[0]["supplier_discount_pct"], 20.0)  # 20.0 instead of 20.00
            
            # Test with float (0.34) - should convert to int
            config.ROUND_TO_DEC_DIGIT = 0.34
            prices = self.processor.calculate_prices()
            # Should work, converting 0.34 to 0 (rounds to integer)
            self.assertEqual(len(prices), 1)
            # With digits=0, values should be rounded to integers
            self.assertEqual(prices[0]["supplier_discount_pct"], 20.0)  # 20.0 instead of 20.00
            
        finally:
            config.ROUND_TO_DEC_DIGIT = original_value

    def test_calculate_prices_limit(self):
        """Test calculate_prices with limit."""
        for i in range(5):
            article = Article(
                article_no  = f"ART{i:03d}",
                name        = f"Article {i}",
                price_type  = 1,
                price_value = 100.0 + i,
                unit        = "PCS",
                raw_line    = f"A;N;ART{i:03d};Article {i};;PCS;1;1;{100.0 + i}",
            )
            self.processor._upsert_article(article)

        prices = self.processor.calculate_prices(limit=3)
        self.assertEqual(len(prices), 3)

    def test_calculate_prices_specific_article(self):
        """Test calculate_prices for specific article."""
        for i in range(3):
            article = Article(
                article_no  = f"ART{i:03d}",
                name        = f"Article {i}",
                price_type  = 1,
                price_value = 100.0 + i,
                unit        = "PCS",
                raw_line    = f"A;N;ART{i:03d};Article {i};;PCS;1;1;{100.0 + i}",
            )
            self.processor._upsert_article(article)

        prices = self.processor.calculate_prices(article_no="ART001")
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["article_no"], "ART001")

    def test_calculate_prices_no_articles(self):
        """Test calculate_prices returns empty list when no articles exist."""
        prices = self.processor.calculate_prices()
        self.assertEqual(len(prices), 0)
        self.assertEqual(prices, [])

    def test_calculate_prices_list_price_zero(self):
        """Test calculate_prices handles list_price=0 correctly (no division by zero)."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 0.0,  # list_price = 0
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;0.0",
        )
        self.processor._upsert_article(article)

        # Add purchase price
        article2 = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 2,
            price_value = 80.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;2;1;80.0",
        )
        self.processor._upsert_article(article2)

        prices = self.processor.calculate_prices()
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["list_price"], 0.0)
        self.assertEqual(prices[0]["purchase_price"], 80.0)
        # supplier_discount_pct should be None when list_price = 0 (division by zero protection)
        self.assertIsNone(prices[0]["supplier_discount_pct"])

    def test_calculate_prices_calculated_purchase_zero(self):
        """Test calculate_prices handles calculated_purchase=0 correctly (no division by zero)."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 2,
            price_value = 0.0,  # purchase_price = 0
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;2;1;0.0",
        )
        self.processor._upsert_article(article)

        prices = self.processor.calculate_prices(overhead_percent=10.0)
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["purchase_price"], 0.0)
        self.assertEqual(prices[0]["calculated_purchase_price"], 0.0)
        self.assertEqual(prices[0]["sale_price"], 0.0)
        # markup_pct should be None when calculated_purchase = 0 (division by zero protection)
        self.assertIsNone(prices[0]["markup_pct"])

    def test_calculate_prices_multiple_steps_same_base_type(self):
        """Test calculate_prices with multiple steps having same base_price_type."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = None,
            price_value = None,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;;;",
        )
        self.processor._upsert_article(article)

        # Add multiple steps with same base_price_type=1
        step1 = PriceStep(
            article_no      = "ART001",
            step_code       = "01",
            description     = "Step 1",
            price_kind      = 1,
            sign            = "+",
            base_price_type = 1,
            value           = 100.0,
            min_quantity    = 1.0,
            max_quantity    = 10.0,
            raw_line        = "Z;N;ART001;01;1;Step 1;Step 1;1;+;1;1;100.0;;1;1.0;10.0",
        )
        self.processor._upsert_price_step(step1)

        step2 = PriceStep(
            article_no      = "ART001",
            step_code       = "02",
            description     = "Step 2",
            price_kind      = 1,
            sign            = "+",
            base_price_type = 1,  # Same base_price_type
            value           = 90.0,
            min_quantity    = 11.0,
            max_quantity    = 20.0,
            raw_line        = "Z;N;ART001;02;1;Step 2;Step 2;1;+;1;1;90.0;;1;11.0;20.0",
        )
        self.processor._upsert_price_step(step2)

        # Test quantity in first range
        prices = self.processor.calculate_prices(quantity=5.0)
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["list_price"], 100.0)  # From step 01

        # Test quantity in second range
        prices = self.processor.calculate_prices(quantity=15.0)
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0]["list_price"], 90.0)  # From step 02

        # Test quantity outside ranges - should use first step (lowest min_quantity)
        prices = self.processor.calculate_prices(quantity=0.5)
        self.assertEqual(len(prices), 1)
        # Should use base_list_price from _first_price_from_steps (first matching step)
        self.assertEqual(prices[0]["list_price"], 100.0)

    def test_first_price_from_steps(self):
        """Test _first_price_from_steps helper method."""
        steps = [
            (2, "+", 1, 50.0, 1.0, 10.0),  # Wrong price_kind
            (1, "+", 2, 80.0, 1.0, 10.0),  # Wrong base_price_type
            (1, "+", 1, 100.0, 1.0, 10.0),  # Correct
            (1, "+", 1, 90.0, 11.0, 20.0),  # Correct but later
        ]
        result = DatanormProcessor._first_price_from_steps(steps, base_price_type=1)
        self.assertEqual(result, 100.0)

    def test_price_from_steps_by_quantity(self):
        """Test _price_from_steps_by_quantity helper method."""
        steps = [
            (1, "+", 1, 100.0, 1.0, 10.0),
            (1, "+", 1, 90.0, 11.0, 20.0),
            (1, "+", 1, 80.0, 21.0, None),  # None means infinity
        ]
        # Test quantity in first range
        result = DatanormProcessor._price_from_steps_by_quantity(steps, base_price_type=1, quantity=5.0)
        self.assertEqual(result, 100.0)

        # Test quantity in second range
        result = DatanormProcessor._price_from_steps_by_quantity(steps, base_price_type=1, quantity=15.0)
        self.assertEqual(result, 90.0)

        # Test quantity in third range
        result = DatanormProcessor._price_from_steps_by_quantity(steps, base_price_type=1, quantity=25.0)
        self.assertEqual(result, 80.0)

        # Test quantity outside all ranges
        result = DatanormProcessor._price_from_steps_by_quantity(steps, base_price_type=1, quantity=0.5)
        self.assertIsNone(result)

    def test_export_prices_to_csv(self):
        """Test export_prices_to_csv creates CSV file."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            self.processor.export_prices_to_csv(temp_path)
            self.assertTrue(temp_path.exists())
            content = temp_path.read_text(encoding="utf-8")
            self.assertIn("article_no", content)
            self.assertIn("ART001", content)
        finally:
            temp_path.unlink()

    def test_export_prices_to_csv_article_no_with_limit(self):
        """Test export_prices_to_csv with article_no and limit combination."""
        # Create multiple articles
        for i in range(5):
            article = Article(
                article_no  = f"ART{i:03d}",
                name        = f"Article {i}",
                price_type  = 1,
                price_value = 100.0 + i,
                unit        = "PCS",
                raw_line    = f"A;N;ART{i:03d};Article {i};;PCS;1;1;{100.0 + i}",
            )
            self.processor._upsert_article(article)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Test: article_no="ART001" with limit=1 should return only ART001
            self.processor.export_prices_to_csv(temp_path, article_no="ART001", limit=1)
            self.assertTrue(temp_path.exists())
            content = temp_path.read_text(encoding="utf-8")
            lines = content.strip().split("\n")
            # Header + 1 data row
            self.assertEqual(len(lines), 2)
            self.assertIn("ART001", content)
            self.assertNotIn("ART002", content)
            self.assertNotIn("ART003", content)

            # Test: article_no="ART001" with limit=2 should still return only ART001
            # (because article_no filters to specific article, limit doesn't apply)
            self.processor.export_prices_to_csv(temp_path, article_no="ART001", limit=2)
            content = temp_path.read_text(encoding="utf-8")
            lines = content.strip().split("\n")
            self.assertEqual(len(lines), 2)  # Still only ART001
            self.assertIn("ART001", content)
            self.assertNotIn("ART002", content)
        finally:
            temp_path.unlink()

    def test_load_file_utf8_encoding(self):
        """Test load_file with UTF-8 encoding (Russian characters)."""
        # Create file with Russian characters in UTF-8
        with tempfile.NamedTemporaryFile(mode="w", suffix=".001", encoding="utf-8", delete=False) as f:
            f.write("A;N;ART001;Товар для теста;;PCS;1;1;100.0\n")
            temp_path = Path(f.name)

        try:
            processor = DatanormProcessor()
            processor.load_file(temp_path, encoding="utf-8")
            article = processor.lookup_article("ART001")
            self.assertIsNotNone(article)
            assert article is not None
            self.assertEqual(article["name"], "Товар для теста")
        finally:
            temp_path.unlink()

    def test_load_file_windows1251_encoding(self):
        """Test load_file with Windows-1251 encoding (Russian characters)."""
        # Create file with Russian characters in Windows-1251
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".001", delete=False) as f:
            f.write("A;N;ART001;Товар для теста;;PCS;1;1;100.0\n".encode("windows-1251"))
            temp_path = Path(f.name)

        try:
            processor = DatanormProcessor()
            processor.load_file(temp_path, encoding="windows-1251")
            article = processor.lookup_article("ART001")
            self.assertIsNotNone(article)
            assert article is not None
            self.assertEqual(article["name"], "Товар для теста")
        finally:
            temp_path.unlink()

    def test_export_prices_to_csv_with_quantity(self):
        """Test export_prices_to_csv includes total prices when quantity is specified."""
        article = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)

        # Add purchase price
        article2 = Article(
            article_no  = "ART001",
            name        = "Test Article",
            price_type  = 2,
            price_value = 80.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Test Article;;PCS;2;1;80.0",
        )
        self.processor._upsert_article(article2)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Export with quantity
            self.processor.export_prices_to_csv(temp_path, quantity=200.0)
            self.assertTrue(temp_path.exists())
            content = temp_path.read_text(encoding="utf-8")
            lines = content.strip().split("\n")
            
            # Check header includes total price fields
            self.assertIn("quantity", content)
            self.assertIn("total_list_price", content)
            self.assertIn("total_purchase_price", content)
            self.assertIn("total_sale_price", content)
            
            # Check data includes total prices
            self.assertIn("200.0", content)
            self.assertIn("20000.0", content)  # 100.0 * 200
            self.assertIn("16000.0", content)  # 80.0 * 200
            
            # Export without quantity - total price fields should not be present
            self.processor.export_prices_to_csv(temp_path)
            content = temp_path.read_text(encoding="utf-8")
            self.assertNotIn("quantity", content)
            self.assertNotIn("total_list_price", content)
        finally:
            temp_path.unlink()

    def test_export_prices_to_csv_utf8_encoding(self):
        """Test export_prices_to_csv with UTF-8 encoding (Russian characters)."""
        article = Article(
            article_no  = "ART001",
            name        = "Товар для теста",
            price_type  = 1,
            price_value = 100.0,
            unit        = "PCS",
            raw_line    = "A;N;ART001;Товар для теста;;PCS;1;1;100.0",
        )
        self.processor._upsert_article(article)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            self.processor.export_prices_to_csv(temp_path, encoding="utf-8")
            self.assertTrue(temp_path.exists())
            content = temp_path.read_text(encoding="utf-8")
            self.assertIn("Товар для теста", content)
            self.assertIn("ART001", content)
        finally:
            temp_path.unlink()

    def test_fetch_prices(self):
        """Test fetch_prices convenience function."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".001", delete=False) as f:
            f.write("A;N;ART001;Test Article;;PCS;1;1;100.0\n")
            temp_path = Path(f.name)

        try:
            processor, prices = fetch_prices(temp_path, overhead_percent=10.0)
            self.assertIsNotNone(processor)
            self.assertEqual(len(prices), 1)
            self.assertEqual(prices[0]["article_no"], "ART001")
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    unittest.main()

