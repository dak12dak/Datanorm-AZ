"""
Mermaid Diagram to SVG Converter

Converts Mermaid diagram files (.mmd) to SVG format using Mermaid CLI.

Usage:
    # Convert Mermaid diagram (SVG will be generated in the same folder)
    python -m tools.mmd2svg file.mmd

    # Convert with explicit output path
    python -m tools.mmd2svg file.mmd --svg output.svg

    # Specify background color
    python -m tools.mmd2svg file.mmd --background transparent

Requirements:
    - Mermaid CLI (mmdc): Install with `npm install -g @mermaid-js/mermaid-cli`
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

MARKDOWN_ENCODING = "utf-8"  # Expected encoding for files


def check_command(command: str) -> bool:
    """Check if a command is available in the system PATH."""
    return shutil.which(command) is not None


def convert_mmd_to_svg(mmd_path: Path, svg_path: Path, background: str = "transparent") -> None:
    """
    Convert Mermaid diagram file to SVG using Mermaid CLI.
    
    Args:
        mmd_path: Path to input .mmd file
        svg_path: Path to output .svg file
        background: Background color for SVG (default: "transparent")
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If Mermaid CLI is not installed
        subprocess.CalledProcessError: If conversion fails
    """
    if not mmd_path.exists():
        raise FileNotFoundError(f"Mermaid file {mmd_path} not found")
    
    if not check_command("mmdc"):
        raise RuntimeError(
            "Mermaid CLI (mmdc) is not installed. "
            "Please install it with: npm install -g @mermaid-js/mermaid-cli"
        )
    
    # On Windows, shell=True may be needed for mmdc
    use_shell = sys.platform == "win32"
    
    # Remove existing SVG file if it exists to ensure clean output
    try:
        svg_path.unlink()
    except FileNotFoundError:
        pass
    
    # Run mmdc command
    subprocess.run(
        ["mmdc", "-i", str(mmd_path), "-o", str(svg_path), "-b", background],
        check=True,
        shell=use_shell,
    )
    
    # Mermaid CLI may create numbered files (e.g., cli_logic-1.svg) instead of the specified name
    # The numbered file name is typically based on the input file stem (e.g., file.mmd -> file-1.svg)
    # The file location depends on mmdc behavior:
    # - Usually creates files in the output directory (specified by -o)
    # - Sometimes may create files in the input directory (observed in some versions/situations)
    # - The numbered suffix (-1) is added when mmdc can't use the exact output filename
    # Check all possible locations to handle different mmdc behaviors
    
    svg_stem = svg_path.stem
    svg_dir  = svg_path.parent
    mmd_stem = mmd_path.stem
    mmd_dir  = mmd_path.parent
    
    # Possible numbered file locations to check
    # 1. Output directory, based on output stem: {svg_stem}-1.svg
    numbered_svg_output_stem = svg_dir / f"{svg_stem}-1.svg"
    # 2. Output directory, based on input stem: {mmd_stem}-1.svg
    numbered_svg_output_input_stem = svg_dir / f"{mmd_stem}-1.svg"
    # 3. Input directory, based on input stem: {mmd_stem}-1.svg
    numbered_svg_input_stem = mmd_dir / f"{mmd_stem}-1.svg"
    # 4. Input directory, based on output stem: {svg_stem}-1.svg (unlikely but possible)
    numbered_svg_input_output_stem = mmd_dir / f"{svg_stem}-1.svg"
    
    # Check all possible locations
    for numbered_svg in [
        numbered_svg_output_stem,
        numbered_svg_output_input_stem,
        numbered_svg_input_stem,
        numbered_svg_input_output_stem,
    ]:
        if numbered_svg.exists():
            if not svg_path.exists():
                # Move/rename numbered file to target location
                if numbered_svg.parent == svg_path.parent:
                    # Same directory, just rename
                    numbered_svg.rename(svg_path)
                else:
                    # Different directory, move
                    numbered_svg.rename(svg_path)
                break  # Found and handled, no need to check others
            else:
                # Target already exists, remove numbered file
                try:
                    numbered_svg.unlink()
                except FileNotFoundError:
                    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Mermaid diagram file to SVG format.",
    )
    parser.add_argument(
        "mmd_file",
        type=Path,
        help="Source Mermaid diagram file (SVG will be generated in the same folder with .svg extension).",
    )
    parser.add_argument(
        "--svg",
        type=Path,
        help="Output SVG file (default: same as input file with .svg extension).",
    )
    parser.add_argument(
        "--background",
        type=str,
        default="transparent",
        help="Background color for SVG (default: transparent).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mmd_path = args.mmd_file
    svg_path = args.svg if args.svg else mmd_path.with_suffix(".svg")
    
    convert_mmd_to_svg(mmd_path, svg_path, args.background)
    print(f"SVG generated: {svg_path}")


if __name__ == "__main__":
    main()

