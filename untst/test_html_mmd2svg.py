"""Tests for html_mmd2svg module.

Test Coverage:

Tested:

Utility functions:
- replace_mmd_with_svg() - mermaid block found with auto-detected SVG,
  mermaid block found with explicit SVG path, mermaid block found but SVG not exists,
  multiple mermaid blocks, no mermaid blocks, different mermaid block formats,
  SVG path detection (_chart.svg and .svg patterns)

Main function:
- main() - file not found (raises FileNotFoundError), successful replacement,
  no changes (no mermaid blocks), no changes (SVG not found), with explicit SVG path

Not Tested:
- parse_args() - tested indirectly through main, but not directly
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import html_mmd2svg


class TestReplaceMmdWithSvg(unittest.TestCase):
    """Test replace_mmd_with_svg function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.html_path = Path(self.temp_dir) / "test.html"
        self.svg_path_chart = Path(self.temp_dir) / "test_chart.svg"
        self.svg_path_simple = Path(self.temp_dir) / "test.svg"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_replace_mmd_with_svg_auto_detected_chart(self):
        """Test replace_mmd_with_svg replaces block with auto-detected _chart.svg."""
        html_content = """<h1>Title</h1>
<pre class="mermaid"><code>flowchart TD
    A --> B
</code></pre>
<p>Text</p>"""
        
        # Create SVG file
        self.svg_path_chart.write_text("<svg>test</svg>", encoding="utf-8")
        
        result = html_mmd2svg.replace_mmd_with_svg(html_content, self.html_path)
        
        self.assertIn('<img src="test_chart.svg"', result)
        self.assertNotIn('<pre class="mermaid"', result)
        self.assertIn("<h1>Title</h1>", result)
        self.assertIn("<p>Text</p>", result)

    def test_replace_mmd_with_svg_auto_detected_simple(self):
        """Test replace_mmd_with_svg uses .svg if _chart.svg not found."""
        html_content = """<pre class="mermaid">flowchart TD
    A --> B
</pre>"""
        
        # Create only simple SVG file (no _chart version)
        self.svg_path_simple.write_text("<svg>test</svg>", encoding="utf-8")
        
        result = html_mmd2svg.replace_mmd_with_svg(html_content, self.html_path)
        
        self.assertIn('<img src="test.svg"', result)
        self.assertNotIn('<pre class="mermaid"', result)

    def test_replace_mmd_with_svg_explicit_path(self):
        """Test replace_mmd_with_svg uses explicit SVG path when provided."""
        html_content = """<pre class="mermaid">flowchart TD
    A --> B
</pre>"""
        
        custom_svg = Path(self.temp_dir) / "custom.svg"
        custom_svg.write_text("<svg>custom</svg>", encoding="utf-8")
        
        result = html_mmd2svg.replace_mmd_with_svg(
            html_content, self.html_path, svg_path=custom_svg
        )
        
        self.assertIn('<img src="custom.svg"', result)
        self.assertNotIn('<pre class="mermaid"', result)

    def test_replace_mmd_with_svg_svg_not_found(self):
        """Test replace_mmd_with_svg returns original when SVG not found."""
        html_content = """<h1>Title</h1>
<pre class="mermaid">flowchart TD
    A --> B
</pre>
<p>Text</p>"""
        
        # Don't create SVG file
        
        result = html_mmd2svg.replace_mmd_with_svg(html_content, self.html_path)
        
        # Should return original content unchanged
        self.assertEqual(result, html_content)
        self.assertIn('<pre class="mermaid"', result)

    def test_replace_mmd_with_svg_explicit_path_not_found(self):
        """Test replace_mmd_with_svg returns original when explicit SVG path doesn't exist."""
        html_content = """<pre class="mermaid">flowchart TD
    A --> B
</pre>"""
        
        nonexistent_svg = Path(self.temp_dir) / "nonexistent.svg"
        
        result = html_mmd2svg.replace_mmd_with_svg(
            html_content, self.html_path, svg_path=nonexistent_svg
        )
        
        # Should return original content unchanged
        self.assertEqual(result, html_content)

    def test_replace_mmd_with_svg_multiple_blocks(self):
        """Test replace_mmd_with_svg replaces multiple Mermaid blocks."""
        html_content = """<h1>Title</h1>
<pre class="mermaid">flowchart TD
    A --> B
</pre>
<p>Text</p>
<pre class="mermaid">graph LR
    X --> Y
</pre>"""
        
        self.svg_path_chart.write_text("<svg>test</svg>", encoding="utf-8")
        
        result = html_mmd2svg.replace_mmd_with_svg(html_content, self.html_path)
        
        # Should have two img tags
        self.assertEqual(result.count('<img src="test_chart.svg"'), 2)
        self.assertEqual(result.count('<pre class="mermaid"'), 0)

    def test_replace_mmd_with_svg_no_blocks(self):
        """Test replace_mmd_with_svg returns unchanged when no Mermaid blocks."""
        html_content = """<h1>Title</h1>
<p>Some text</p>
<pre class="python">print("hello")</pre>"""
        
        result = html_mmd2svg.replace_mmd_with_svg(html_content, self.html_path)
        
        # Should return unchanged
        self.assertEqual(result, html_content)

    def test_replace_mmd_with_svg_different_class_format(self):
        """Test replace_mmd_with_svg handles different class attribute formats."""
        html_content = """<pre class='mermaid'>flowchart TD
    A --> B
</pre>"""
        
        self.svg_path_chart.write_text("<svg>test</svg>", encoding="utf-8")
        
        result = html_mmd2svg.replace_mmd_with_svg(html_content, self.html_path)
        
        self.assertIn('<img src="test_chart.svg"', result)
        self.assertNotIn("class='mermaid'", result)

    def test_replace_mmd_with_svg_priority_chart_over_simple(self):
        """Test replace_mmd_with_svg prefers _chart.svg over .svg."""
        html_content = """<pre class="mermaid">flowchart TD
    A --> B
</pre>"""
        
        # Create both SVG files
        self.svg_path_chart.write_text("<svg>chart</svg>", encoding="utf-8")
        self.svg_path_simple.write_text("<svg>simple</svg>", encoding="utf-8")
        
        result = html_mmd2svg.replace_mmd_with_svg(html_content, self.html_path)
        
        # Should use _chart.svg (first in candidates list)
        self.assertIn('<img src="test_chart.svg"', result)
        self.assertNotIn('test.svg', result)


class TestMain(unittest.TestCase):
    """Test main function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.html_path = Path(self.temp_dir) / "test.html"
        self.svg_path = Path(self.temp_dir) / "test_chart.svg"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("tools.html_mmd2svg.parse_args")
    def test_main_file_not_found(self, mock_parse_args):
        """Test main raises FileNotFoundError when file doesn't exist."""
        nonexistent = Path(self.temp_dir) / "nonexistent.html"
        
        args = Mock()
        args.html_file = nonexistent
        args.svg = None
        mock_parse_args.return_value = args
        
        with self.assertRaises(FileNotFoundError) as context:
            html_mmd2svg.main()
        
        self.assertIn("not found", str(context.exception))

    @patch("tools.html_mmd2svg.parse_args")
    @patch("builtins.print")
    def test_main_successful_replacement(self, mock_print, mock_parse_args):
        """Test main successfully replaces Mermaid blocks."""
        html_content = """<h1>Title</h1>
<pre class="mermaid">flowchart TD
    A --> B
</pre>"""
        self.html_path.write_text(html_content, encoding="utf-8")
        self.svg_path.write_text("<svg>test</svg>", encoding="utf-8")
        
        args = Mock()
        args.html_file = self.html_path
        args.svg = None
        mock_parse_args.return_value = args
        
        html_mmd2svg.main()
        
        # Check file was updated
        updated_content = self.html_path.read_text(encoding="utf-8")
        self.assertIn('<img src="test_chart.svg"', updated_content)
        self.assertNotIn('<pre class="mermaid"', updated_content)
        
        # Check print was called
        mock_print.assert_called_once()
        self.assertIn("Updated", str(mock_print.call_args))

    @patch("tools.html_mmd2svg.parse_args")
    @patch("builtins.print")
    def test_main_no_changes_no_mermaid(self, mock_print, mock_parse_args):
        """Test main reports no changes when no Mermaid blocks found."""
        html_content = """<h1>Title</h1>
<p>Some text</p>"""
        self.html_path.write_text(html_content, encoding="utf-8")
        
        args = Mock()
        args.html_file = self.html_path
        args.svg = None
        mock_parse_args.return_value = args
        
        html_mmd2svg.main()
        
        # Check file was not changed
        updated_content = self.html_path.read_text(encoding="utf-8")
        self.assertEqual(updated_content, html_content)
        
        # Check print was called with "No changes"
        mock_print.assert_called_once()
        self.assertIn("No changes", str(mock_print.call_args))

    @patch("tools.html_mmd2svg.parse_args")
    @patch("builtins.print")
    def test_main_no_changes_svg_not_found(self, mock_print, mock_parse_args):
        """Test main reports no changes when SVG not found."""
        html_content = """<pre class="mermaid">flowchart TD
    A --> B
</pre>"""
        self.html_path.write_text(html_content, encoding="utf-8")
        # Don't create SVG file
        
        args = Mock()
        args.html_file = self.html_path
        args.svg = None
        mock_parse_args.return_value = args
        
        html_mmd2svg.main()
        
        # Check file was not changed
        updated_content = self.html_path.read_text(encoding="utf-8")
        self.assertEqual(updated_content, html_content)
        
        # Check print was called with "No changes"
        mock_print.assert_called_once()
        self.assertIn("No changes", str(mock_print.call_args))

    @patch("tools.html_mmd2svg.parse_args")
    @patch("builtins.print")
    def test_main_with_explicit_svg(self, mock_print, mock_parse_args):
        """Test main uses explicit SVG path when provided."""
        html_content = """<pre class="mermaid">flowchart TD
    A --> B
</pre>"""
        self.html_path.write_text(html_content, encoding="utf-8")
        
        custom_svg = Path(self.temp_dir) / "custom.svg"
        custom_svg.write_text("<svg>custom</svg>", encoding="utf-8")
        
        args = Mock()
        args.html_file = self.html_path
        args.svg = custom_svg
        mock_parse_args.return_value = args
        
        html_mmd2svg.main()
        
        # Check file was updated with custom SVG
        updated_content = self.html_path.read_text(encoding="utf-8")
        self.assertIn('<img src="custom.svg"', updated_content)
        
        mock_print.assert_called_once()
        self.assertIn("Updated", str(mock_print.call_args))


if __name__ == "__main__":
    unittest.main()

