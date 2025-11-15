"""Tests for main module.

Test Coverage:

Tested:
- Export path handling with default_output_folder:
  - Relative path prepends default_output_folder
  - Absolute path ignores default_output_folder
  - Intermediate folders are created automatically
  - Output folder is created if it doesn't exist
- Export mode:
  - Export with --article flag
  - Export with --prices flag
  - Export without --article/--prices (with limit)
  - Parameters passed correctly (overhead, quantity)
- Article lookup mode (--article without --export):
  - Article found - prints JSON
  - Article not found - raises SystemExit
- Prices lookup mode (--prices without --export):
  - Prices found - prints JSON
  - Prices not found - raises SystemExit
- Default mode (--limit == 1):
  - First article exists - prints article + prices
  - No articles - prints empty array
- List mode (--limit != 1):
  - Multiple articles with calculated prices
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
import main


class TestExportPathHandling(unittest.TestCase):
    """Test export path handling with default_output_folder."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_output_folder = config.default_output_folder
        # Use temp directory for testing
        config.default_output_folder = str(self.temp_dir / "output")

    def tearDown(self):
        """Clean up test fixtures."""
        config.default_output_folder = self.original_output_folder
        # Clean up temp directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_relative_path_prepends_default_output_folder(self, mock_print, mock_parse_args, mock_processor_class):
        """Test that relative path is prepended with default_output_folder."""
        # Setup mocks
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = Path("test.csv")
        args.article = None
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        # Run main
        main.main()

        # Verify export_prices_to_csv was called with correct path
        expected_path = Path(config.default_output_folder) / "test.csv"
        mock_processor.export_prices_to_csv.assert_called_once()
        call_args = mock_processor.export_prices_to_csv.call_args
        self.assertEqual(call_args[0][0], expected_path)
        
        # Verify folder was created
        self.assertTrue(expected_path.parent.exists())
        
        # Verify print message
        mock_print.assert_called_with(f"Exported results to {expected_path}")

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_absolute_path_ignores_default_output_folder(self, mock_print, mock_parse_args, mock_processor_class):
        """Test that absolute path ignores default_output_folder."""
        # Setup mocks
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        absolute_path = self.temp_dir / "absolute_test.csv"
        args = Mock()
        args.file = Path("test.dat")
        args.export = absolute_path
        args.article = None
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        # Run main
        main.main()

        # Verify export_prices_to_csv was called with absolute path (unchanged)
        mock_processor.export_prices_to_csv.assert_called_once()
        call_args = mock_processor.export_prices_to_csv.call_args
        self.assertEqual(call_args[0][0], absolute_path)
        
        # Verify print message
        mock_print.assert_called_with(f"Exported results to {absolute_path}")

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_nested_path_creates_intermediate_folders(self, mock_print, mock_parse_args, mock_processor_class):
        """Test that nested paths create intermediate folders."""
        # Setup mocks
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = Path("subfolder/nested/test.csv")
        args.article = None
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        # Run main
        main.main()

        # Verify export_prices_to_csv was called
        expected_path = Path(config.default_output_folder) / "subfolder/nested/test.csv"
        mock_processor.export_prices_to_csv.assert_called_once()
        call_args = mock_processor.export_prices_to_csv.call_args
        self.assertEqual(call_args[0][0], expected_path)
        
        # Verify intermediate folders were created
        self.assertTrue(expected_path.parent.exists())
        self.assertTrue((expected_path.parent.parent).exists())

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_output_folder_created_if_not_exists(self, mock_print, mock_parse_args, mock_processor_class):
        """Test that output folder is created if it doesn't exist."""
        # Setup mocks
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Use a non-existent folder
        config.default_output_folder = str(self.temp_dir / "new_output_folder")
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = Path("test.csv")
        args.article = None
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        # Verify folder doesn't exist before
        output_folder = Path(config.default_output_folder)
        self.assertFalse(output_folder.exists())

        # Run main
        main.main()

        # Verify folder was created
        self.assertTrue(output_folder.exists())


class TestExportMode(unittest.TestCase):
    """Test export mode functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_output_folder = config.default_output_folder
        config.default_output_folder = str(self.temp_dir / "output")

    def tearDown(self):
        """Clean up test fixtures."""
        config.default_output_folder = self.original_output_folder
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_export_with_article_flag(self, mock_print, mock_parse_args, mock_processor_class):
        """Test export mode with --article flag."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = Path("test.csv")
        args.article = "ART001"
        args.prices = None
        args.overhead = 5.0
        args.quantity = 100.0
        args.limit = 1
        mock_parse_args.return_value = args

        main.main()

        # Verify export_prices_to_csv called with article_no
        mock_processor.export_prices_to_csv.assert_called_once()
        call_kwargs = mock_processor.export_prices_to_csv.call_args[1]
        self.assertEqual(call_kwargs["article_no"], "ART001")
        self.assertEqual(call_kwargs["overhead_percent"], 5.0)
        self.assertEqual(call_kwargs["quantity"], 100.0)

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_export_with_prices_flag(self, mock_print, mock_parse_args, mock_processor_class):
        """Test export mode with --prices flag."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = Path("test.csv")
        args.article = None
        args.prices = "ART002"
        args.overhead = 10.0
        args.quantity = 50.0
        args.limit = 1
        mock_parse_args.return_value = args

        main.main()

        # Verify export_prices_to_csv called with article_no from prices
        mock_processor.export_prices_to_csv.assert_called_once()
        call_kwargs = mock_processor.export_prices_to_csv.call_args[1]
        self.assertEqual(call_kwargs["article_no"], "ART002")
        self.assertEqual(call_kwargs["overhead_percent"], 10.0)
        self.assertEqual(call_kwargs["quantity"], 50.0)

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_export_without_article_or_prices(self, mock_print, mock_parse_args, mock_processor_class):
        """Test export mode without --article or --prices (uses limit)."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = Path("test.csv")
        args.article = None
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 5
        mock_parse_args.return_value = args

        main.main()

        # Verify export_prices_to_csv called with limit
        mock_processor.export_prices_to_csv.assert_called_once()
        call_kwargs = mock_processor.export_prices_to_csv.call_args[1]
        self.assertIsNone(call_kwargs.get("article_no"))
        self.assertEqual(call_kwargs["limit"], 5)


class TestArticleLookupMode(unittest.TestCase):
    """Test article lookup mode (--article without --export)."""

    @patch("main.align_json_colons")
    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_article_lookup_found(self, mock_print, mock_parse_args, mock_processor_class, mock_align):
        """Test article lookup when article is found."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        article_data = {"article_no": "ART001", "name": "Test Article"}
        mock_processor.lookup_article.return_value = article_data
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = None
        args.article = "ART001"
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        mock_align.return_value = '{"article_no": "ART001"}'

        main.main()

        # Verify lookup_article was called
        mock_processor.lookup_article.assert_called_once_with("ART001")
        # Verify JSON was formatted and printed
        mock_align.assert_called_once()
        mock_print.assert_called_once()

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    def test_article_lookup_not_found(self, mock_parse_args, mock_processor_class):
        """Test article lookup when article is not found (raises SystemExit)."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.lookup_article.return_value = None
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = None
        args.article = "NOTFOUND"
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        with self.assertRaises(SystemExit):
            main.main()


class TestPricesLookupMode(unittest.TestCase):
    """Test prices lookup mode (--prices without --export)."""

    @patch("main.align_json_colons")
    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_prices_lookup_found(self, mock_print, mock_parse_args, mock_processor_class, mock_align):
        """Test prices lookup when prices are found."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        prices_data = [{"article_no": "ART001", "sale_price": 100.0}]
        mock_processor.calculate_prices.return_value = prices_data
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = None
        args.article = None
        args.prices = "ART001"
        args.overhead = 5.0
        args.quantity = 10.0
        args.limit = 1
        mock_parse_args.return_value = args

        mock_align.return_value = '[{"article_no": "ART001"}]'

        main.main()

        # Verify calculate_prices was called with correct parameters
        mock_processor.calculate_prices.assert_called_once_with(
            overhead_percent=5.0, article_no="ART001", quantity=10.0
        )
        # Verify JSON was formatted and printed
        mock_align.assert_called_once()
        mock_print.assert_called_once()

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    def test_prices_lookup_not_found(self, mock_parse_args, mock_processor_class):
        """Test prices lookup when article is not found (raises SystemExit)."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.calculate_prices.return_value = []
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = None
        args.article = None
        args.prices = "NOTFOUND"
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        with self.assertRaises(SystemExit):
            main.main()


class TestDefaultMode(unittest.TestCase):
    """Test default mode (--limit == 1, no other flags)."""

    @patch("main.align_json_colons")
    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_default_mode_article_exists(self, mock_print, mock_parse_args, mock_processor_class, mock_align):
        """Test default mode when first article exists."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Mock get_first_article_no result
        mock_processor.get_first_article_no.return_value = "ART001"
        mock_processor.lookup_article.return_value = {"article_no": "ART001", "name": "Test"}
        mock_processor.calculate_prices.return_value = [{"article_no": "ART001", "sale_price": 100.0}]
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = None
        args.article = None
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        mock_align.return_value = '{"article": {...}, "prices": {...}}'

        main.main()

        # Verify get_first_article_no was called
        mock_processor.get_first_article_no.assert_called_once()
        # Verify lookup_article and calculate_prices were called
        mock_processor.lookup_article.assert_called_once_with("ART001")
        mock_processor.calculate_prices.assert_called_once_with(
            overhead_percent=0.0, article_no="ART001", quantity=None
        )
        # Verify JSON was formatted and printed
        mock_align.assert_called_once()
        mock_print.assert_called_once()

    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_default_mode_no_articles(self, mock_print, mock_parse_args, mock_processor_class):
        """Test default mode when no articles exist (prints empty array)."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Mock get_first_article_no returns None (no articles)
        mock_processor.get_first_article_no.return_value = None
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = None
        args.article = None
        args.prices = None
        args.overhead = 0.0
        args.quantity = None
        args.limit = 1
        mock_parse_args.return_value = args

        main.main()

        # Verify get_first_article_no was called
        mock_processor.get_first_article_no.assert_called_once()
        # Verify print was called with empty array
        mock_print.assert_called_once_with("[]")


class TestListMode(unittest.TestCase):
    """Test list mode (--limit != 1, no other flags)."""

    @patch("main.align_json_colons")
    @patch("main.DatanormProcessor")
    @patch("main.parse_args")
    @patch("builtins.print")
    def test_list_mode_multiple_articles(self, mock_print, mock_parse_args, mock_processor_class, mock_align):
        """Test list mode with multiple articles."""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        prices_data = [
            {"article_no": "ART001", "sale_price": 100.0},
            {"article_no": "ART002", "sale_price": 200.0},
        ]
        mock_processor.calculate_prices.return_value = prices_data
        
        args = Mock()
        args.file = Path("test.dat")
        args.export = None
        args.article = None
        args.prices = None
        args.overhead = 10.0
        args.quantity = 5.0
        args.limit = 10
        mock_parse_args.return_value = args

        mock_align.return_value = '[{"article_no": "ART001"}, ...]'

        main.main()

        # Verify calculate_prices was called with limit
        mock_processor.calculate_prices.assert_called_once_with(
            overhead_percent=10.0, limit=10, quantity=5.0
        )
        # Verify JSON was formatted and printed
        mock_align.assert_called_once()
        mock_print.assert_called_once()


if __name__ == "__main__":
    unittest.main()

