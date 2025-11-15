"""Command-line argument parser for Datanorm-AZ processor."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import config


def limit_type(value: str) -> Optional[int]:
    """Parse limit argument: integer, 'None', or 'all' for unlimited."""
    if value.lower() in ("none", "all"):
        return None
    try:
        limit = int(value)
        if limit < 0:
            raise argparse.ArgumentTypeError("limit must be non-negative")
        return limit
    except ValueError:
        raise argparse.ArgumentTypeError(f"limit must be an integer, 'None', or 'all', got: {value}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for Datanorm-AZ processor."""
    parser = argparse.ArgumentParser(
        description="Parse DATANORM files, load data into an in-memory database and calculate sales prices.",
    )
    parser.add_argument(
        "file",
        type=Path,
        nargs="?",
        default=Path(config.datafile),
        help=f"Path to the DATANORM file (default: {config.datafile}).",
    )
    parser.add_argument(
        "--overhead",
        type=float,
        default=0.0,
        help="Overhead percentage applied on top of purchase price (default: 0).",
    )
    parser.add_argument(
        "--article",
        type=str,
        help="Look up a single article number (returns raw data without price calculations).",
    )
    parser.add_argument(
        "--prices",
        type=str,
        help="Get calculated prices for a single article number.",
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Export calculated prices to CSV at the given path.",
    )
    parser.add_argument(
        "--limit",
        type=limit_type,
        default=1,
        help="Limit number of articles when printing to stdout (default: 1). Use 'None' or 'all' for unlimited.",
    )
    parser.add_argument(
        "--qnt",
        type=float,
        dest="quantity",
        help="Quantity for price calculation (uses graduated prices if available).",
    )
    return parser.parse_args()

