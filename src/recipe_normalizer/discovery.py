"""Discover recipe files in a directory."""

from collections.abc import Iterator
from pathlib import Path

from recipe_normalizer.parsers import SUPPORTED_SUFFIXES

# Stable scan order so CLI output does not depend on filesystem readdir.
_SUFFIX_PRIORITY = {
    ".yaml": 0,
    ".yml": 0,
    ".xml": 1,
    ".json": 2,
    ".toml": 3,
}


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
    return sorted(
        files,
        key=lambda path: (
            _SUFFIX_PRIORITY.get(path.suffix.lower(), 99),
            str(path).lower(),
        ),
    )
