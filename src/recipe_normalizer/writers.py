"""Serialize recipes to JSON."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from recipe_normalizer.models import Recipe


def recipes_to_json(recipes: Sequence[Recipe]) -> str:
    payload = [recipe.to_dict() for recipe in recipes]
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_recipes(recipes: Sequence[Recipe], destination: Path | TextIO) -> None:
    text = recipes_to_json(recipes)
    if isinstance(destination, Path):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        return
    destination.write(text)
