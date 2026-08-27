"""Serialize recipes to JSON."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, TextIO

from recipe_normalizer.models import Recipe


def _dump_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))


def recipes_to_json(recipes: Sequence[Recipe]) -> str:
    """Pretty-print recipes with compact ingredient objects.

    Formatting follows the provided expected_output.json: tab-indented recipe
    objects, with each ingredient on a single line.
    """
    blocks: list[str] = []
    for recipe in recipes:
        data = recipe.to_dict()
        ingredient_items = data["ingredients"]
        if ingredient_items:
            ingredient_body = ",\n".join(
                f"\t\t\t{_dump_compact(item)}" for item in ingredient_items
            )
            ingredients_json = f"[\n{ingredient_body}\n\t\t]"
        else:
            ingredients_json = "[]"

        preparation_items = data["preparations"]
        if preparation_items:
            preparation_body = ",\n".join(
                f"\t\t\t{_dump_compact(step)}" for step in preparation_items
            )
            preparations_json = f"[\n{preparation_body}\n\t\t]"
        else:
            preparations_json = "[]"

        blocks.append(
            "\t{\n"
            f'\t\t"name": {_dump_compact(data["name"])},\n'
            f'\t\t"ingredients": {ingredients_json},\n'
            f'\t\t"preparations": {preparations_json}\n'
            "\t}"
        )
    return "[\n" + ",\n".join(blocks) + "\n]\n"


def write_recipes(recipes: Sequence[Recipe], destination: Path | TextIO) -> None:
    text = recipes_to_json(recipes)
    if isinstance(destination, Path):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        return
    destination.write(text)
