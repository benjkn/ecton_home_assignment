"""Domain errors for the recipe normalizer."""

from pathlib import Path


class RecipeNormalizerError(Exception):
    """Base error for the recipe normalizer."""


class ParseError(RecipeNormalizerError):
    """Raised when a recipe file cannot be parsed into the internal model."""

    def __init__(self, message: str, path: Path | None = None) -> None:
        self.path = path
        prefix = f"{path}: " if path is not None else ""
        super().__init__(f"{prefix}{message}")
