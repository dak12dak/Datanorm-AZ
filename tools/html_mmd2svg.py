"""
Replace Mermaid code blocks in HTML files with SVG image references.

This script post-processes HTML files generated from Markdown to replace
Mermaid diagram code blocks with <img> tags pointing to corresponding SVG files.

Usage:
    # Process a single HTML file
    python -m tools.html_mmd2svg file.html

    # Process with explicit SVG path
    python -m tools.html_mmd2svg file.html --svg diagram.svg

Requirements:
    - None (pure Python, uses standard library only)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Optional

MARKDOWN_ENCODING = "utf-8"  # Expected encoding for HTML files


def replace_mmd_with_svg(html_content: str, html_path: Path, svg_path: Optional[Path] = None) -> str:
    """
    Replace Mermaid code blocks in HTML with SVG image references.
    
    Looks for Mermaid code blocks (typically in <pre class="mermaid"> tags)
    and replaces them with <img> tags pointing to corresponding SVG files.
    
    Args:
        html_content: HTML content to process
        html_path: Path to the HTML file (used to determine SVG path if svg_path not provided)
        svg_path: Optional explicit path to SVG file. If not provided, searches for SVG files
                  with pattern: {html_stem}_chart.svg or {html_stem}.svg
        
    Returns:
        HTML content with Mermaid blocks replaced by image tags
    """
    # Pattern to match Mermaid code blocks (pandoc creates <pre class="mermaid"><code>...</code></pre>)
    # Also handles other possible formats
    mermaid_pattern = r'<pre[^>]*class=["\']mermaid["\'][^>]*>.*?</pre>'
    
    def replace_match(match: re.Match) -> str:
        """Replace Mermaid block with SVG image if SVG file exists."""
        # Determine SVG path
        if svg_path:
            target_svg = svg_path
        else:
            # Try to find corresponding SVG file
            # Pattern: if HTML is cli_logic.html, look for cli_logic_chart.svg
            html_stem = html_path.stem
            svg_candidates = [
                html_path.parent / f"{html_stem}_chart.svg",
                html_path.parent / f"{html_stem}.svg",
            ]
            
            # Find first existing SVG candidate
            target_svg = None
            for candidate in svg_candidates:
                if candidate.exists():
                    target_svg = candidate
                    break
            
            if not target_svg:
                # If SVG not found, return original block
                return match.group(0)
        
        # Check if SVG exists
        if not target_svg.exists():
            return match.group(0)
        
        # Use relative path from HTML to SVG
        relative_svg = target_svg.name
        return f'<p><img src="{relative_svg}" alt="Flowchart diagram" style="max-width: 100%; height: auto;" /></p>'
    
    # Replace all Mermaid blocks
    result = re.sub(mermaid_pattern, replace_match, html_content, flags=re.DOTALL | re.IGNORECASE)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replace Mermaid code blocks in HTML with SVG image references.",
    )
    parser.add_argument(
        "html_file",
        type=Path,
        help="HTML file to process (will be modified in place).",
    )
    parser.add_argument(
        "--svg",
        type=Path,
        help="Explicit path to SVG file. If not provided, searches for {html_stem}_chart.svg or {html_stem}.svg in the same directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    html_path = args.html_file
    
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file {html_path} not found")
    
    # Read HTML content
    html_content = html_path.read_text(encoding=MARKDOWN_ENCODING)
    
    # Replace Mermaid blocks with SVG images
    updated_content = replace_mmd_with_svg(html_content, html_path, args.svg)
    
    # Write back if changed
    if updated_content != html_content:
        html_path.write_text(updated_content, encoding=MARKDOWN_ENCODING)
        print(f"Updated: {html_path} (Mermaid blocks replaced with SVG images)")
    else:
        print(f"No changes: {html_path} (no Mermaid blocks found or SVG not available)")


if __name__ == "__main__":
    main()

