"""Tests for md2html module.

Test Coverage:

Tested:

Utility functions:
- check_command() - command exists, command not exists
- fix_md_links_to_html() - replaces .md links with .html links in href attributes

Conversion functions:
- convert_with_pandoc() - basic conversion
- convert_with_nodejs() - Linux platform, Windows platform, encoding parameter,
  wrong encoding raises UnicodeDecodeError

Main conversion function:
- render_html() - with pandoc converter, with node converter,
  pandoc not installed (raises RuntimeError), node not installed (raises RuntimeError),
  file not found (raises FileNotFoundError), custom style file, wrong encoding raises UnicodeDecodeError,
  fixes .md links to .html links

Main function:
- main() - specified converter, auto-detect pandoc, fallback to node when pandoc fails,
  non-standard file extensions

Not Tested:
- check_file_encoding() - tested indirectly through render_html, but not directly
  (chardet available/unavailable scenarios, low confidence cases)
- parse_args() - tested indirectly through main, but not directly
- convert_with_pandoc_via_temp() - internal function, tested through render_html
- set_style() - internal function, tested through render_html
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import md2html


class TestCheckCommand(unittest.TestCase):
    """Test check_command function."""

    @patch("tools.md2html.shutil.which")
    def test_check_command_exists(self, mock_which):
        """Test check_command returns True when command exists."""
        mock_which.return_value = "/usr/bin/pandoc"
        self.assertTrue(md2html.check_command("pandoc"))
        mock_which.assert_called_once_with("pandoc")

    @patch("tools.md2html.shutil.which")
    def test_check_command_not_exists(self, mock_which):
        """Test check_command returns False when command doesn't exist."""
        mock_which.return_value = None
        self.assertFalse(md2html.check_command("nonexistent"))
        mock_which.assert_called_once_with("nonexistent")


class TestConvertWithPandoc(unittest.TestCase):
    """Test convert_with_pandoc function."""

    @patch("tools.md2html.subprocess.run")
    def test_convert_with_pandoc(self, mock_run):
        """Test pandoc conversion."""
        md_path = Path("test.md")
        html_path = Path("test.html")
        
        # Mock subprocess.run
        mock_run.return_value = None
        
        # Mock Path.read_text
        with patch.object(Path, "read_text", return_value="<html>test</html>"):
            result = md2html.convert_with_pandoc(md_path, html_path)
        
        mock_run.assert_called_once_with(
            ["pandoc", str(md_path), "-o", str(html_path)],
            check=True,
        )
        self.assertEqual(result, "<html>test</html>")


class TestConvertWithNodejs(unittest.TestCase):
    """Test convert_with_nodejs function."""

    @patch("tools.md2html.subprocess.run")
    @patch("sys.platform", "linux")
    def test_convert_with_nodejs_linux(self, mock_run):
        """Test node.js conversion on Linux."""
        md_path = Path("test.md")
        md_content = "# Test"
        
        # Mock Path.read_text
        with patch.object(Path, "read_text", return_value=md_content):
            mock_result = Mock()
            mock_result.stdout = "<h1>Test</h1>"
            mock_run.return_value = mock_result
            
            result = md2html.convert_with_nodejs(md_path)
        
        mock_run.assert_called_once_with(
            ["npx", "--yes", "marked"],
            input=md_content,
            text=True,
            encoding=md2html.MARKDOWN_ENCODING,
            capture_output=True,
            check=True,
            shell=False,
        )
        self.assertEqual(result, "<h1>Test</h1>")

    @patch("tools.md2html.subprocess.run")
    @patch("sys.platform", "win32")
    def test_convert_with_nodejs_windows(self, mock_run):
        """Test node.js conversion on Windows."""
        md_path = Path("test.md")
        md_content = "# Test"
        
        # Mock Path.read_text
        with patch.object(Path, "read_text", return_value=md_content):
            mock_result = Mock()
            mock_result.stdout = "<h1>Test</h1>"
            mock_run.return_value = mock_result
            
            result = md2html.convert_with_nodejs(md_path)
        
        mock_run.assert_called_once_with(
            ["npx", "--yes", "marked"],
            input=md_content,
            text=True,
            encoding=md2html.MARKDOWN_ENCODING,
            capture_output=True,
            check=True,
            shell=True,
        )
        self.assertEqual(result, "<h1>Test</h1>")


class TestFixMdLinksToHtml(unittest.TestCase):
    """Test fix_md_links_to_html function."""

    def test_fix_md_links_double_quotes(self):
        """Test replacing .md links with .html in double quotes."""
        html = '<a href="file.md">Link</a>'
        result = md2html.fix_md_links_to_html(html)
        self.assertEqual(result, '<a href="file.html">Link</a>')

    def test_fix_md_links_single_quotes(self):
        """Test replacing .md links with .html in single quotes."""
        html = "<a href='file.md'>Link</a>"
        result = md2html.fix_md_links_to_html(html)
        self.assertEqual(result, "<a href='file.html'>Link</a>")

    def test_fix_md_links_multiple(self):
        """Test replacing multiple .md links."""
        html = '<a href="file1.md">Link1</a> <a href="path/to/file2.md">Link2</a>'
        result = md2html.fix_md_links_to_html(html)
        self.assertEqual(result, '<a href="file1.html">Link1</a> <a href="path/to/file2.html">Link2</a>')

    def test_fix_md_links_no_md_extension(self):
        """Test that non-.md links are not changed."""
        html = '<a href="file.html">Link</a> <a href="file.txt">Link</a>'
        result = md2html.fix_md_links_to_html(html)
        self.assertEqual(result, html)

    def test_fix_md_links_no_links(self):
        """Test that HTML without links is unchanged."""
        html = "<h1>Title</h1><p>Text</p>"
        result = md2html.fix_md_links_to_html(html)
        self.assertEqual(result, html)


class TestRenderHtml(unittest.TestCase):
    """Test render_html function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.md_path = Path(self.temp_dir) / "test.md"
        self.html_path = Path(self.temp_dir) / "test.html"
        self.md_path.write_text("# Test", encoding="utf-8")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("tools.md2html.check_command")
    @patch("tools.md2html.convert_with_pandoc")
    @patch("tools.md2html.tempfile.NamedTemporaryFile")
    def test_render_html_with_pandoc(self, mock_tempfile, mock_convert, mock_check):
        """Test render_html with pandoc converter."""
        mock_check.return_value = True
        mock_convert.return_value = '<h1>Test</h1><a href="file.md">Link</a>'
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = str(self.html_path)
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        md2html.render_html(self.md_path, self.html_path, converter="pandoc")
        
        mock_check.assert_called_once_with("pandoc")
        self.assertTrue(self.html_path.exists())
        content = self.html_path.read_text(encoding="utf-8")
        self.assertIn("<style>", content)
        self.assertIn("<h1>Test</h1>", content)
        # Check that .md links are replaced with .html
        self.assertIn('href="file.html"', content)
        self.assertNotIn('href="file.md"', content)

    @patch("tools.md2html.check_command")
    @patch("tools.md2html.convert_with_nodejs")
    def test_render_html_with_node(self, mock_convert, mock_check):
        """Test render_html with node converter."""
        mock_check.return_value = True
        mock_convert.return_value = '<h1>Test</h1><a href="file.md">Link</a>'
        
        md2html.render_html(self.md_path, self.html_path, converter="node")
        
        mock_check.assert_called_once_with("node")
        self.assertTrue(self.html_path.exists())
        content = self.html_path.read_text(encoding="utf-8")
        self.assertIn("<style>", content)
        self.assertIn("<h1>Test</h1>", content)
        # Check that .md links are replaced with .html
        self.assertIn('href="file.html"', content)
        self.assertNotIn('href="file.md"', content)

    @patch("tools.md2html.check_command")
    def test_render_html_pandoc_not_installed(self, mock_check):
        """Test render_html raises error when pandoc not installed."""
        mock_check.return_value = False
        
        with self.assertRaises(RuntimeError) as context:
            md2html.render_html(self.md_path, self.html_path, converter="pandoc")
        
        self.assertIn("pandoc is not installed", str(context.exception))

    @patch("tools.md2html.check_command")
    def test_render_html_node_not_installed(self, mock_check):
        """Test render_html raises error when node not installed."""
        mock_check.return_value = False
        
        with self.assertRaises(RuntimeError) as context:
            md2html.render_html(self.md_path, self.html_path, converter="node")
        
        self.assertIn("node.js is not installed", str(context.exception))

    def test_render_html_file_not_found(self):
        """Test render_html raises error when markdown file doesn't exist."""
        nonexistent = Path(self.temp_dir) / "nonexistent.md"
        
        with self.assertRaises(FileNotFoundError):
            md2html.render_html(nonexistent, self.html_path)

    @patch("tools.md2html.check_command")
    @patch("tools.md2html.convert_with_pandoc")
    @patch("tools.md2html.tempfile.NamedTemporaryFile")
    def test_render_html_with_custom_style(self, mock_tempfile, mock_convert, mock_check):
        """Test render_html with custom style file."""
        mock_check.return_value = True
        mock_convert.return_value = "<h1>Test</h1>"
        
        style_path = Path(self.temp_dir) / "custom.css"
        style_path.write_text("body { color: red; }", encoding="utf-8")
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = str(self.html_path)
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        md2html.render_html(self.md_path, self.html_path, style_path=style_path, converter="pandoc")
        
        content = self.html_path.read_text(encoding="utf-8")
        self.assertIn("body { color: red; }", content)

    def test_convert_with_nodejs_wrong_encoding_raises_error(self):
        """Test convert_with_nodejs raises UnicodeDecodeError for wrong encoding."""
        # Create file with Windows-1251 encoding (Russian text)
        wrong_encoding_file = Path(self.temp_dir) / "wrong_encoding.md"
        with wrong_encoding_file.open("wb") as f:
            # Write Cyrillic text in Windows-1251 encoding
            # "тест" in Windows-1251: 0xF2 0xE5 0xF1 0xF2
            f.write(b"Test: \xF2\xE5\xF1\xF2")
        
        # Should raise UnicodeDecodeError when trying to read as UTF-8
        with self.assertRaises(UnicodeDecodeError):
            md2html.convert_with_nodejs(wrong_encoding_file)

    @patch("tools.md2html.check_command")
    def test_render_html_wrong_encoding_nodejs_raises_error(self, mock_check):
        """Test render_html with node.js raises UnicodeDecodeError for wrong encoding."""
        mock_check.return_value = True
        
        # Create file with Windows-1251 encoding
        wrong_encoding_file = Path(self.temp_dir) / "wrong_encoding.md"
        with wrong_encoding_file.open("wb") as f:
            # Write Cyrillic text in Windows-1251 encoding
            # "тест" in Windows-1251: 0xF2 0xE5 0xF1 0xF2
            f.write(b"Test: \xF2\xE5\xF1\xF2")
        
        # convert_with_nodejs will try to read as UTF-8 and fail
        with self.assertRaises(UnicodeDecodeError):
            md2html.render_html(wrong_encoding_file, self.html_path, converter="node")


class TestMain(unittest.TestCase):
    """Test main function."""

    @patch("tools.md2html.render_html")
    @patch("tools.md2html.parse_args")
    @patch("builtins.print")
    def test_main_with_specified_converter(self, mock_print, mock_parse_args, mock_render):
        """Test main with explicitly specified converter."""
        args = Mock()
        args.md_file = Path("test.md")
        args.html = None
        args.style = None
        args.converter = "pandoc"
        mock_parse_args.return_value = args
        
        md2html.main()
        
        mock_render.assert_called_once_with(
            args.md_file, Path("test.html"), None, "pandoc"
        )

    @patch("tools.md2html.render_html")
    @patch("tools.md2html.parse_args")
    @patch("builtins.print")
    def test_main_auto_detect_pandoc(self, mock_print, mock_parse_args, mock_render):
        """Test main auto-detects pandoc."""
        args = Mock()
        args.md_file = Path("test.md")
        args.html = None
        args.style = None
        args.converter = None
        mock_parse_args.return_value = args
        
        md2html.main()
        
        # Should try pandoc first
        mock_render.assert_called_once_with(
            args.md_file, Path("test.html"), None, "pandoc"
        )

    @patch("tools.md2html.render_html")
    @patch("tools.md2html.parse_args")
    @patch("builtins.print")
    def test_main_auto_detect_fallback_to_node(self, mock_print, mock_parse_args, mock_render):
        """Test main falls back to node when pandoc fails."""
        args = Mock()
        args.md_file = Path("test.md")
        args.html = None
        args.style = None
        args.converter = None
        mock_parse_args.return_value = args
        
        # First call (pandoc) raises error, second (node) succeeds
        mock_render.side_effect = [RuntimeError("pandoc not found"), None]
        
        md2html.main()
        
        # Should try both converters
        self.assertEqual(mock_render.call_count, 2)
        mock_render.assert_any_call(args.md_file, Path("test.html"), None, "pandoc")
        mock_render.assert_any_call(args.md_file, Path("test.html"), None, "node")

    @patch("tools.md2html.render_html")
    @patch("tools.md2html.parse_args")
    @patch("builtins.print")
    def test_main_with_non_standard_extension(self, mock_print, mock_parse_args, mock_render):
        """Test main handles files with non-standard extensions."""
        args = Mock()
        args.md_file = Path("test_file.not-md")
        args.html = None
        args.style = None
        args.converter = "pandoc"
        mock_parse_args.return_value = args
        
        md2html.main()
        
        # Should replace extension with .html
        expected_md_path = Path("test_file.not-md")
        expected_html_path = Path("test_file.html")
        mock_render.assert_called_once_with(
            expected_md_path, expected_html_path, None, "pandoc"
        )


if __name__ == "__main__":
    unittest.main()

