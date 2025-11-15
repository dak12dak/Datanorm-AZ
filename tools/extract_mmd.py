"""
Mermaid Diagram Extractor

Extracts Mermaid diagram blocks from Markdown files and saves them as .mmd files.
If multiple Mermaid blocks are found, extracts all of them to separate files.

Usage:
    # Extract mermaid diagram(s) (MMD will be generated in the same folder)
    python -m tools.extract_mmd file.md

    # Extract with explicit output path (if multiple blocks, uses numbered suffixes)
    python -m tools.extract_mmd file.md --mmd output.mmd

    # Extract and automatically convert to SVG (all blocks if multiple found)
    python -m tools.extract_mmd file.md --svg output.svg

Output example (if multiple diagrams found):
    MMD extracted (3 diagrams):
      - file.mmd
      - file-2.mmd
      - file-3.mmd

Requirements:
    - None (pure Python, uses standard library only)
    - Mermaid CLI (mmdc) if --svg option is used: Install with `npm install -g @mermaid-js/mermaid-cli`
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List

MARKDOWN_ENCODING = "utf-8"  # Expected encoding for Markdown files


def extract_mermaid_blocks(md_content: str) -> List[str]:
    """
    Extract all Mermaid diagram blocks from Markdown content.
    
    Looks for code blocks with ```mermaid ... ``` syntax.
    
    Args:
        md_content: Markdown file content
        
    Returns:
        List of extracted Mermaid diagram contents (without ```mermaid markers).
        Returns empty list if no blocks found.
    """
    # Pattern to match mermaid code blocks
    # Matches: ```mermaid ... ``` or ``` mermaid ... ```
    pattern = r"```\s*mermaid\s*\n(.*?)```"
    matches = re.findall(pattern, md_content, re.DOTALL)
    
    return [match.strip() for match in matches]


def generate_output_paths(base_path: Path, count: int) -> List[Path]:
    """
    Generate output file paths for multiple diagrams.
    
    If count is 1, returns [base_path].
    If count > 1, returns [base_path, base_path-2, base_path-3, ...].
    
    Args:
        base_path: Base output path
        count: Number of diagrams
        
    Returns:
        List of output paths
    """
    if count == 1:
        return [base_path]
    
    paths = [base_path]
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    
    for i in range(2, count + 1):
        numbered_path = parent / f"{stem}-{i}{suffix}"
        paths.append(numbered_path)
    
    return paths


def extract_mmd(md_path: Path, mmd_path: Path) -> List[Path]:
    """
    Extract all Mermaid diagrams from Markdown file and save to .mmd files.
    
    If multiple diagrams are found, saves them to numbered files:
    - First: mmd_path
    - Second: mmd_path-2
    - Third: mmd_path-3
    - etc.
    
    Args:
        md_path: Path to input Markdown file
        mmd_path: Path to output .mmd file (base path for multiple files)
        
    Returns:
        List of created .mmd file paths
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If no Mermaid block found in the file
    """
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file {md_path} not found")
    
    md_content = md_path.read_text(encoding=MARKDOWN_ENCODING)
    mermaid_blocks = extract_mermaid_blocks(md_content)
    
    if not mermaid_blocks:
        raise ValueError(f"No Mermaid diagram block found in {md_path}")
    
    # Generate output paths for all blocks
    output_paths = generate_output_paths(mmd_path, len(mermaid_blocks))
    
    # Remove existing MMD files if they exist to ensure clean output
    for path in output_paths:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    
    # Write all blocks to their respective files
    for content, path in zip(mermaid_blocks, output_paths):
        path.write_text(content, encoding=MARKDOWN_ENCODING)
    
    return output_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Mermaid diagram from Markdown file and save as .mmd file.",
    )
    parser.add_argument(
        "md_file",
        type=Path,
        help="Source Markdown file (MMD will be generated in the same folder with .mmd extension).",
    )
    parser.add_argument(
        "--mmd",
        type=Path,
        help="Output MMD file (default: same as input file with .mmd extension).",
    )
    parser.add_argument(
        "--svg",
        type=Path,
        help="Output SVG file (automatically converts MMD to SVG after extraction).",
    )
    parser.add_argument(
        "--background",
        type=str,
        default="transparent",
        help="Background color for SVG (default: transparent). Only used with --svg option.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    md_path = args.md_file
    mmd_path = args.mmd if args.mmd else md_path.with_suffix(".mmd")
    
    # Extract all Mermaid blocks
    mmd_paths = extract_mmd(md_path, mmd_path)
    
    # Print extraction results
    if len(mmd_paths) == 1:
        print(f"MMD extracted: {mmd_paths[0]}")
    else:
        print(f"MMD extracted ({len(mmd_paths)} diagrams):")
        for path in mmd_paths:
            print(f"  - {path}")
    
    # If --svg option is specified, automatically convert all to SVG
    if args.svg:
        # Import here to avoid circular dependencies
        from tools.mmd2svg import convert_mmd_to_svg
        
        # Generate SVG paths for all MMD files
        svg_paths = generate_output_paths(args.svg, len(mmd_paths))
        
        # Convert each MMD to SVG
        for mmd_p, svg_p in zip(mmd_paths, svg_paths):
            convert_mmd_to_svg(mmd_p, svg_p, args.background)
        
        # Print conversion results
        if len(svg_paths) == 1:
            print(f"SVG generated: {svg_paths[0]}")
        else:
            print(f"SVG generated ({len(svg_paths)} files):")
            for path in svg_paths:
                print(f"  - {path}")


if __name__ == "__main__":
    main()

