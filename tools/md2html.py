"""
Markdown to HTML Converter

Converts Markdown files to HTML with optional CSS style injection.
Supports two conversion backends: pandoc (preferred) and node.js with marked library.

Usage:
    # Convert a Markdown file (HTML will be generated in the same folder)
    python -m tools.md2html file.md

    # Convert with explicit output path
    python -m tools.md2html file.md --html output.html

    # Use specific converter
    python -m tools.md2html file.md --converter pandoc
    python -m tools.md2html file.md --converter node

    # Add custom CSS style
    python -m tools.md2html file.md --style custom.css

Requirements:
    - pandoc (https://pandoc.org/installing.html) OR
    - node.js (https://nodejs.org/) with npx (marked will be installed automatically)
    - chardet (optional, recommended): For better encoding detection and warnings
      Install with: pip install chardet
      If not available, the module will use a simpler encoding check.

Known Limitations:
    - Leading spaces in code blocks: Both pandoc and node.js (marked) require proper
      code block syntax (triple backticks) to preserve formatting. Plain text with
      leading spaces will be treated as regular paragraphs.
    - Lists without an empty line before them:
      * pandoc: May not recognize lists without an empty line before them
      * node.js (marked): Successfully recognizes lists even without an empty line

Testing:
    Run unit tests with:
    python -m unittest untst.test_md2html -v
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import argparse
import re
import shutil
import subprocess
import tempfile
import warnings

MARKDOWN_ENCODING = "utf-8"  # Expected encoding for Markdown files

DEFAULT_STYLE = """<style>
table {
  border-collapse: collapse;
  width: 100%;
}
th, td {
  text-align: left;
  padding: 6px 10px;
  vertical-align: top;
  border: 1px solid #ccc;
}
thead th {
  background-color: #f5f5f5;
}
pre, code {
  white-space: pre-wrap;
}
/* For PDF export: `pandoc <input.md> -o <output.pdf> --pdf-engine=xelatex -V mainfont="Arial"` */
</style>
"""


def check_command(command: str) -> bool:
    """Check if a command is available in the system PATH."""
    return shutil.which(command) is not None


def check_file_encoding(file_path: Path) -> None:
    """
    Check if file encoding matches expected MARKDOWN_ENCODING.
    Issues a warning if encoding differs.
    """
    try:
        # Try to detect encoding using chardet if available
        try:
            import chardet
            with file_path.open("rb") as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                detected_encoding_raw = detected.get("encoding")
                detected_encoding = detected_encoding_raw.lower() if detected_encoding_raw else ""
                expected_encoding = MARKDOWN_ENCODING.lower()
                
                # ASCII is a subset of UTF-8, so it's compatible
                if detected_encoding and detected_encoding not in (expected_encoding, "ascii"):
                    confidence = detected.get("confidence", 0)
                    if confidence > 0.7:  # Only warn if confidence is high
                        warnings.warn(
                            f"File {file_path} appears to be encoded as {detected_encoding_raw} "
                            f"(confidence: {confidence:.1%}), but {MARKDOWN_ENCODING} is expected. "
                            f"Conversion may fail or produce incorrect results.",
                            UserWarning,
                            stacklevel=2,
                        )
        except ImportError:
            # chardet not available, try to read as UTF-8 with strict error handling
            try:
                file_path.read_text(encoding=MARKDOWN_ENCODING, errors="strict")
            except UnicodeDecodeError:
                warnings.warn(
                    f"File {file_path} cannot be read as {MARKDOWN_ENCODING}. "
                    f"It may be in a different encoding. Conversion may fail.",
                    UserWarning,
                    stacklevel=2,
                )
    except Exception:
        # If file doesn't exist or other error, skip check (will be handled elsewhere)
        pass


def convert_with_pandoc(md_path: Path, html_path: Path) -> str:
    """Convert Markdown to HTML using pandoc."""
    subprocess.run(
        ["pandoc", str(md_path), "-o", str(html_path)],
        check=True,
    )
    return html_path.read_text(encoding=MARKDOWN_ENCODING)


def convert_with_nodejs(md_path: Path) -> str:
    """Convert Markdown to HTML using node.js with marked (via npx)."""
    md_content = md_path.read_text(encoding=MARKDOWN_ENCODING)
    
    # Use npx marked (automatically installs marked if not available)
    # On Windows native, shell=True may be needed for npx
    # In WSL (Windows Subsystem for Linux), sys.platform is 'linux', so shell=False is correct
    import sys
    use_shell = sys.platform == "win32"
    
    result = subprocess.run(
        ["npx", "--yes", "marked"],
        input=md_content,
        text=True,
        encoding=MARKDOWN_ENCODING,
        capture_output=True,
        check=True,
        shell=use_shell,
    )
    return result.stdout


def fix_md_links_to_html(html_content: str) -> str:
    """
    Replace .md file extensions with .html in href attributes.
    
    Converts links like href="file.md" to href="file.html" so that
    HTML version of README links to HTML versions of other files.
    """
    # Pattern to match href attributes pointing to .md files
    # Matches: href="path/to/file.md" or href='path/to/file.md'
    pattern = r'(href=["\'])([^"\']+\.md)(["\'])'
    
    def replace_md_with_html(match: re.Match) -> str:
        """Replace .md with .html in href attribute."""
        quote_start = match.group(1)  # " or '
        path = match.group(2)  # path/to/file.md
        quote_end = match.group(3)  # " or '
        
        # Replace .md with .html
        new_path = path.replace('.md', '.html')
        return f"{quote_start}{new_path}{quote_end}"
    
    # Replace all href="...md" with href="...html"
    result = re.sub(pattern, replace_md_with_html, html_content)
    return result


def render_html(
    md_path: Path, html_path: Path, style_path: Optional[Path] = None, converter: str = "pandoc"
) -> None:
    """Convert Markdown to HTML using specified converter (pandoc or node)."""
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file {md_path} not found")
    
    # Check file encoding and warn if it differs from expected
    check_file_encoding(md_path)

    def convert_with_pandoc_via_temp() -> str:
        """Convert using pandoc via temporary file."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp_file:
            tmp_html_path = Path(tmp_file.name)
        try:
            return convert_with_pandoc(md_path, tmp_html_path)
        finally:
            try:
                tmp_html_path.unlink()
            except FileNotFoundError:
                pass

    def set_style(style_path: Optional[Path]) -> str:
        """Get style content from file or use default."""
        if style_path:
            return style_path.read_text(encoding=MARKDOWN_ENCODING)
        else:
            return DEFAULT_STYLE

    # Check converter availability and convert
    if converter == "pandoc":
        if not check_command("pandoc"):
            raise RuntimeError("pandoc is not installed. Please install it from https://pandoc.org/installing.html")
        html_content = convert_with_pandoc_via_temp()
    elif converter == "node":
        if not check_command("node"):
            raise RuntimeError("node.js is not installed. Please install it from https://nodejs.org/")
        html_content = convert_with_nodejs(md_path)
    else:
        raise ValueError(f"Unknown converter: {converter}. Must be 'pandoc' or 'node'.")

    style_content = set_style(style_path)

    if not html_content.lstrip().startswith("<style"):
        html_content = f"{style_content}\n{html_content}"

    # Replace .md links with .html links (works for both pandoc and node converters)
    html_content = fix_md_links_to_html(html_content)

    # Remove existing HTML file if it exists to ensure clean output
    try:
        html_path.unlink()
    except FileNotFoundError:
        pass
    html_path.write_text(html_content, encoding=MARKDOWN_ENCODING)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to HTML with optional style injection.",
    )
    parser.add_argument(
        "md_file",
        type=Path,
        help="Source Markdown file (HTML will be generated in the same folder with .html extension).",
    )
    parser.add_argument(
        "--html",
        type=Path,
        help="Output HTML file (default: same as input file with .html extension).",
    )
    parser.add_argument(
        "--style",
        type=Path,
        help="Optional path to a style snippet inserted at the beginning of the HTML.",
    )
    parser.add_argument(
        "--converter",
        choices=["pandoc", "node"],
        help="Force use of specific converter (pandoc or node). If not specified, auto-detect.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    md_path = args.md_file
    html_path = args.html if args.html else md_path.with_suffix(".html")

    # Try converters: use specified one or auto-detect
    if args.converter:
        converters = [args.converter]
    else:
        converters = ["pandoc", "node"]

    for converter in converters:
        try:
            render_html(md_path, html_path, args.style, converter)
            break
        except RuntimeError:
            continue
    else:
        # All converters failed
        raise RuntimeError(
            "Neither pandoc nor node.js is installed. "
            "Please install one of them to convert Markdown to HTML:\n"
            "  - pandoc: https://pandoc.org/installing.html\n"
            "  - node.js: https://nodejs.org/"
        )

    print(f"HTML generated: {html_path} (using {converter})")


if __name__ == "__main__":
    main()
    