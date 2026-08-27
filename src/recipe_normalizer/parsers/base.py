"""Parser protocol shared by all format adapters."""

from pathlib import Path
from typing import Protocol

from recipe_normalizer.models import Recipe


class Parser(Protocol):
    """Parse a recipe file into one or more Recipe objects."""

    def parse(self, path: Path) -> list[Recipe]:
        """Return recipes contained in ``path``."""
        ...
