"""Tests for extract_mmd module.

Test Coverage:

Tested:

Utility functions:
- extract_mermaid_blocks() - mermaid block found, not found, with spaces in marker,
  multiple blocks (extracts all), empty block, block with extra whitespace
- generate_output_paths() - single path, multiple paths with numbering

Main extraction function:
- extract_mmd() - successful extraction (single and multiple blocks),
  file not found (raises FileNotFoundError), no mermaid block found (raises ValueError),
  overwrites existing files

Main function:
- main() - default output path, explicit --mmd path, with --svg option,
  with --svg and --background options, multiple blocks extraction

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

from tools import extract_mmd


class TestExtractMermaidBlocks(unittest.TestCase):
    """Test extract_mermaid_blocks function."""

    def test_extract_mermaid_blocks_found(self):
        """Test extract_mermaid_blocks finds mermaid block."""
        md_content = """# Title

Some text.

```mermaid
flowchart TD
    A --> B
```

More text."""
        results = extract_mmd.extract_mermaid_blocks(md_content)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertIn("flowchart TD", result)
        self.assertIn("A --> B", result)
        self.assertNotIn("```mermaid", result)
        self.assertNotIn("```", result)

    def test_extract_mermaid_blocks_not_found(self):
        """Test extract_mermaid_blocks returns empty list when no block found."""
        md_content = """# Title

Some text.

```python
print("hello")
```

More text."""
        results = extract_mmd.extract_mermaid_blocks(md_content)
        self.assertEqual(len(results), 0)

    def test_extract_mermaid_blocks_with_spaces(self):
        """Test extract_mermaid_blocks handles spaces in marker."""
        md_content = """# Title

``` mermaid
flowchart TD
    A --> B
```

More text."""
        results = extract_mmd.extract_mermaid_blocks(md_content)
        self.assertEqual(len(results), 1)
        self.assertIn("flowchart TD", results[0])

    def test_extract_mermaid_blocks_multiple_blocks(self):
        """Test extract_mermaid_blocks extracts all blocks when multiple exist."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```

```mermaid
graph LR
    X --> Y
```

More text."""
        results = extract_mmd.extract_mermaid_blocks(md_content)
        self.assertEqual(len(results), 2)
        self.assertIn("A --> B", results[0])
        self.assertIn("X --> Y", results[1])

    def test_extract_mermaid_blocks_empty(self):
        """Test extract_mermaid_blocks handles empty block."""
        md_content = """# Title

```mermaid
```

More text."""
        results = extract_mmd.extract_mermaid_blocks(md_content)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "")

    def test_extract_mermaid_blocks_with_whitespace(self):
        """Test extract_mermaid_blocks trims whitespace."""
        md_content = """# Title

```mermaid
    
    flowchart TD
        A --> B
    
```

More text."""
        results = extract_mmd.extract_mermaid_blocks(md_content)
        self.assertEqual(len(results), 1)
        # Should be trimmed
        self.assertTrue(results[0].startswith("flowchart TD"))


class TestGenerateOutputPaths(unittest.TestCase):
    """Test generate_output_paths function."""

    def test_generate_output_paths_single(self):
        """Test generate_output_paths returns single path for count=1."""
        base_path = Path("output.mmd")
        paths = extract_mmd.generate_output_paths(base_path, 1)
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0], base_path)

    def test_generate_output_paths_multiple(self):
        """Test generate_output_paths generates numbered paths for multiple files."""
        base_path = Path("output.mmd")
        paths = extract_mmd.generate_output_paths(base_path, 3)
        self.assertEqual(len(paths), 3)
        self.assertEqual(paths[0], Path("output.mmd"))
        self.assertEqual(paths[1], Path("output-2.mmd"))
        self.assertEqual(paths[2], Path("output-3.mmd"))

    def test_generate_output_paths_with_directory(self):
        """Test generate_output_paths works with paths in directories."""
        base_path = Path("dir/output.svg")
        paths = extract_mmd.generate_output_paths(base_path, 2)
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0], Path("dir/output.svg"))
        self.assertEqual(paths[1], Path("dir/output-2.svg"))


class TestExtractMmd(unittest.TestCase):
    """Test extract_mmd function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.md_path = Path(self.temp_dir) / "test.md"
        self.mmd_path = Path(self.temp_dir) / "test.mmd"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extract_mmd_successful(self):
        """Test extract_mmd successfully extracts single mermaid block."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```

More text."""
        self.md_path.write_text(md_content, encoding="utf-8")
        
        paths = extract_mmd.extract_mmd(self.md_path, self.mmd_path)
        
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0], self.mmd_path)
        self.assertTrue(self.mmd_path.exists())
        content = self.mmd_path.read_text(encoding="utf-8")
        self.assertIn("flowchart TD", content)
        self.assertIn("A --> B", content)
        self.assertNotIn("```mermaid", content)

    def test_extract_mmd_multiple_blocks(self):
        """Test extract_mmd extracts multiple blocks to numbered files."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```

```mermaid
graph LR
    X --> Y
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        
        paths = extract_mmd.extract_mmd(self.md_path, self.mmd_path)
        
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0], self.mmd_path)
        self.assertEqual(paths[1], self.mmd_path.parent / "test-2.mmd")
        
        # Check first file
        self.assertTrue(self.mmd_path.exists())
        content1 = self.mmd_path.read_text(encoding="utf-8")
        self.assertIn("A --> B", content1)
        
        # Check second file
        self.assertTrue(paths[1].exists())
        content2 = paths[1].read_text(encoding="utf-8")
        self.assertIn("X --> Y", content2)

    def test_extract_mmd_file_not_found(self):
        """Test extract_mmd raises FileNotFoundError when file doesn't exist."""
        nonexistent = Path(self.temp_dir) / "nonexistent.md"
        
        with self.assertRaises(FileNotFoundError) as context:
            extract_mmd.extract_mmd(nonexistent, self.mmd_path)
        
        self.assertIn("not found", str(context.exception))

    def test_extract_mmd_no_mermaid_block(self):
        """Test extract_mmd raises ValueError when no mermaid block found."""
        md_content = """# Title

Some text without mermaid blocks."""
        self.md_path.write_text(md_content, encoding="utf-8")
        
        with self.assertRaises(ValueError) as context:
            extract_mmd.extract_mmd(self.md_path, self.mmd_path)
        
        self.assertIn("No Mermaid diagram block found", str(context.exception))

    def test_extract_mmd_overwrites_existing(self):
        """Test extract_mmd overwrites existing MMD file."""
        # Create existing MMD file
        old_content = "old content"
        self.mmd_path.write_text(old_content, encoding="utf-8")
        
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        
        extract_mmd.extract_mmd(self.md_path, self.mmd_path)
        
        content = self.mmd_path.read_text(encoding="utf-8")
        self.assertIn("flowchart TD", content)
        self.assertNotIn("old content", content)

    def test_extract_mmd_overwrites_multiple_existing(self):
        """Test extract_mmd overwrites multiple existing MMD files."""
        # Create existing numbered files
        old_path1 = self.mmd_path
        old_path2 = self.mmd_path.parent / "test-2.mmd"
        old_path1.write_text("old content 1", encoding="utf-8")
        old_path2.write_text("old content 2", encoding="utf-8")
        
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```

```mermaid
graph LR
    X --> Y
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        
        paths = extract_mmd.extract_mmd(self.md_path, self.mmd_path)
        
        self.assertEqual(len(paths), 2)
        # Check that old content is gone
        content1 = paths[0].read_text(encoding="utf-8")
        content2 = paths[1].read_text(encoding="utf-8")
        self.assertNotIn("old content 1", content1)
        self.assertNotIn("old content 2", content2)
        self.assertIn("A --> B", content1)
        self.assertIn("X --> Y", content2)


class TestMain(unittest.TestCase):
    """Test main function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.md_path = Path(self.temp_dir) / "test.md"
        self.mmd_path = Path(self.temp_dir) / "test.mmd"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("tools.extract_mmd.parse_args")
    @patch("builtins.print")
    def test_main_default_output_path(self, mock_print, mock_parse_args):
        """Test main uses default output path."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        
        args = Mock()
        args.md_file = self.md_path
        args.mmd = None
        args.svg = None
        args.background = "transparent"
        mock_parse_args.return_value = args
        
        extract_mmd.main()
        
        expected_mmd = self.md_path.with_suffix(".mmd")
        self.assertTrue(expected_mmd.exists())
        mock_print.assert_called_once_with(f"MMD extracted: {expected_mmd}")

    @patch("tools.extract_mmd.parse_args")
    @patch("builtins.print")
    def test_main_explicit_mmd_path(self, mock_print, mock_parse_args):
        """Test main uses explicit --mmd path."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        custom_mmd = Path(self.temp_dir) / "custom.mmd"
        
        args = Mock()
        args.md_file = self.md_path
        args.mmd = custom_mmd
        args.svg = None
        args.background = "transparent"
        mock_parse_args.return_value = args
        
        extract_mmd.main()
        
        self.assertTrue(custom_mmd.exists())
        mock_print.assert_called_once_with(f"MMD extracted: {custom_mmd}")

    @patch("tools.extract_mmd.parse_args")
    @patch("tools.mmd2svg.convert_mmd_to_svg")
    @patch("builtins.print")
    def test_main_with_svg_option(self, mock_print, mock_convert, mock_parse_args):
        """Test main converts to SVG when --svg option is specified."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        svg_path = Path(self.temp_dir) / "output.svg"
        
        args = Mock()
        args.md_file = self.md_path
        args.mmd = None
        args.svg = svg_path
        args.background = "transparent"
        mock_parse_args.return_value = args
        
        extract_mmd.main()
        
        expected_mmd = self.md_path.with_suffix(".mmd")
        mock_convert.assert_called_once_with(expected_mmd, svg_path, "transparent")
        self.assertEqual(mock_print.call_count, 2)
        mock_print.assert_any_call(f"MMD extracted: {expected_mmd}")
        mock_print.assert_any_call(f"SVG generated: {svg_path}")

    @patch("tools.extract_mmd.parse_args")
    @patch("tools.mmd2svg.convert_mmd_to_svg")
    @patch("builtins.print")
    def test_main_with_svg_and_background(self, mock_print, mock_convert, mock_parse_args):
        """Test main uses custom background color when specified."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        svg_path = Path(self.temp_dir) / "output.svg"
        
        args = Mock()
        args.md_file = self.md_path
        args.mmd = None
        args.svg = svg_path
        args.background = "white"
        mock_parse_args.return_value = args
        
        extract_mmd.main()
        
        expected_mmd = self.md_path.with_suffix(".mmd")
        mock_convert.assert_called_once_with(expected_mmd, svg_path, "white")

    @patch("tools.extract_mmd.parse_args")
    @patch("builtins.print")
    def test_main_multiple_blocks(self, mock_print, mock_parse_args):
        """Test main handles multiple blocks correctly."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```

```mermaid
graph LR
    X --> Y
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        
        args = Mock()
        args.md_file = self.md_path
        args.mmd = None
        args.svg = None
        args.background = "transparent"
        mock_parse_args.return_value = args
        
        extract_mmd.main()
        
        # Should print list of extracted files (header + 2 files = 3 calls)
        self.assertEqual(mock_print.call_count, 3)
        # Check that it mentions 2 diagrams
        call_args = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("2 diagrams" in str(call) for call in call_args))

    @patch("tools.extract_mmd.parse_args")
    @patch("tools.mmd2svg.convert_mmd_to_svg")
    @patch("builtins.print")
    def test_main_multiple_blocks_with_svg(self, mock_print, mock_convert, mock_parse_args):
        """Test main converts multiple blocks to SVG."""
        md_content = """# Title

```mermaid
flowchart TD
    A --> B
```

```mermaid
graph LR
    X --> Y
```
"""
        self.md_path.write_text(md_content, encoding="utf-8")
        svg_path = Path(self.temp_dir) / "output.svg"
        
        args = Mock()
        args.md_file = self.md_path
        args.mmd = None
        args.svg = svg_path
        args.background = "transparent"
        mock_parse_args.return_value = args
        
        extract_mmd.main()
        
        # Should convert both MMD files to SVG
        self.assertEqual(mock_convert.call_count, 2)
        # Should print MMD extraction (header + 2 files = 3) and SVG generation (header + 2 files = 3) = 6 total
        self.assertEqual(mock_print.call_count, 6)
        # Check that it prints list of SVG files
        call_args = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("2 files" in str(call) for call in call_args))


if __name__ == "__main__":
    unittest.main()

