"""Tests for datanorm_parser module.

Test Coverage:

Tested:
- limit_type():
  - Valid integer values
  - 'None' and 'all' strings (case insensitive)
  - Negative numbers (raises ArgumentTypeError)
  - Invalid strings (raises ArgumentTypeError)
- parse_args():
  - Default arguments (no arguments provided)
  - All argument flags (--article, --prices, --export, --overhead, --limit, --qnt)
  - File argument (positional)
  - Argument combinations
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from datanorm_parser import limit_type, parse_args


class TestLimitType(unittest.TestCase):
    """Test limit_type function."""

    def test_limit_type_valid_integer(self):
        """Test limit_type with valid integer."""
        self.assertEqual(limit_type("5"), 5)
        self.assertEqual(limit_type("0"), 0)
        self.assertEqual(limit_type("100"), 100)

    def test_limit_type_none_string(self):
        """Test limit_type with 'None' string (case insensitive)."""
        self.assertIsNone(limit_type("None"))
        self.assertIsNone(limit_type("none"))
        self.assertIsNone(limit_type("NONE"))

    def test_limit_type_all_string(self):
        """Test limit_type with 'all' string (case insensitive)."""
        self.assertIsNone(limit_type("all"))
        self.assertIsNone(limit_type("All"))
        self.assertIsNone(limit_type("ALL"))

    def test_limit_type_negative_number(self):
        """Test limit_type with negative number (raises ArgumentTypeError)."""
        import argparse
        with self.assertRaises(argparse.ArgumentTypeError) as cm:
            limit_type("-1")
        self.assertIn("non-negative", str(cm.exception))

    def test_limit_type_invalid_string(self):
        """Test limit_type with invalid string (raises ArgumentTypeError)."""
        import argparse
        with self.assertRaises(argparse.ArgumentTypeError) as cm:
            limit_type("invalid")
        self.assertIn("integer, 'None', or 'all'", str(cm.exception))


class TestParseArgs(unittest.TestCase):
    """Test parse_args function."""

    def test_parse_args_default(self):
        """Test parse_args with no arguments (uses defaults)."""
        with patch("sys.argv", ["main.py"]):
            args = parse_args()
            self.assertEqual(args.file, Path(config.datafile))
            self.assertEqual(args.overhead, 0.0)
            self.assertIsNone(args.article)
            self.assertIsNone(args.prices)
            self.assertIsNone(args.export)
            self.assertEqual(args.limit, 1)
            self.assertIsNone(args.quantity)

    def test_parse_args_file_argument(self):
        """Test parse_args with file argument."""
        test_file = Path("test.dat")
        with patch("sys.argv", ["main.py", str(test_file)]):
            args = parse_args()
            self.assertEqual(args.file, test_file)

    def test_parse_args_article_flag(self):
        """Test parse_args with --article flag."""
        with patch("sys.argv", ["main.py", "--article", "ART001"]):
            args = parse_args()
            self.assertEqual(args.article, "ART001")

    def test_parse_args_prices_flag(self):
        """Test parse_args with --prices flag."""
        with patch("sys.argv", ["main.py", "--prices", "ART002"]):
            args = parse_args()
            self.assertEqual(args.prices, "ART002")

    def test_parse_args_export_flag(self):
        """Test parse_args with --export flag."""
        export_path = Path("output.csv")
        with patch("sys.argv", ["main.py", "--export", str(export_path)]):
            args = parse_args()
            self.assertEqual(args.export, export_path)

    def test_parse_args_overhead_flag(self):
        """Test parse_args with --overhead flag."""
        with patch("sys.argv", ["main.py", "--overhead", "10.5"]):
            args = parse_args()
            self.assertEqual(args.overhead, 10.5)

    def test_parse_args_limit_flag(self):
        """Test parse_args with --limit flag."""
        with patch("sys.argv", ["main.py", "--limit", "5"]):
            args = parse_args()
            self.assertEqual(args.limit, 5)

    def test_parse_args_limit_all(self):
        """Test parse_args with --limit all."""
        with patch("sys.argv", ["main.py", "--limit", "all"]):
            args = parse_args()
            self.assertIsNone(args.limit)

    def test_parse_args_limit_none(self):
        """Test parse_args with --limit None."""
        with patch("sys.argv", ["main.py", "--limit", "None"]):
            args = parse_args()
            self.assertIsNone(args.limit)

    def test_parse_args_qnt_flag(self):
        """Test parse_args with --qnt flag."""
        with patch("sys.argv", ["main.py", "--qnt", "100.5"]):
            args = parse_args()
            self.assertEqual(args.quantity, 100.5)

    def test_parse_args_all_flags(self):
        """Test parse_args with all flags combined."""
        test_file = Path("test.dat")
        export_path = Path("output.csv")
        with patch("sys.argv", [
            "main.py",
            str(test_file),
            "--article", "ART001",
            "--export", str(export_path),
            "--overhead", "5.0",
            "--limit", "10",
            "--qnt", "50.0",
        ]):
            args = parse_args()
            self.assertEqual(args.file, test_file)
            self.assertEqual(args.article, "ART001")
            self.assertEqual(args.export, export_path)
            self.assertEqual(args.overhead, 5.0)
            self.assertEqual(args.limit, 10)
            self.assertEqual(args.quantity, 50.0)


if __name__ == "__main__":
    unittest.main()

