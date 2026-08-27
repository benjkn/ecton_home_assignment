"""Transformer protocol."""

from typing import Protocol

from recipe_normalizer.models import Recipe


class Transformer(Protocol):
    """Apply a recipe-level transformation."""

    name: str

    def apply(self, recipe: Recipe) -> Recipe:
        """Return a transformed copy of ``recipe``."""
        ...
