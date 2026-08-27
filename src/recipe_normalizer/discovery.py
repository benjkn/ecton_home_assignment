"""Discover recipe files in a directory."""

from collections.abc import Iterator
from pathlib import Path

from recipe_normalizer.parsers import SUPPORTED_SUFFIXES


def discover_recipe_files(input_dir: Path, *, recursive: bool = False) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    iterator: Iterator[Path]
    if recursive:
        iterator = input_dir.rglob("*")
    else:
        iterator = input_dir.iterdir()

    files = [
        path
        for path in iterator
        if path.is_file()
        and not path.name.startswith(".")
        and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    # Sorted by path so output order does not depend on filesystem readdir order.
    return sorted(files, key=lambda path: str(path).lower())
