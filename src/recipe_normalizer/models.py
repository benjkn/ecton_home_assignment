"""Internal recipe representation and mapping helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from recipe_normalizer.exceptions import ParseError


def as_json_number(value: float | int) -> int | float:
    """Return an int when ``value`` is a whole number, otherwise a float."""
    as_float = float(value)
    if as_float.is_integer():
        return int(as_float)
    return as_float


def parse_quantity(value: Any) -> int | float:
    """Coerce a quantity from XML/YAML/JSON/TOML into a number."""
    if isinstance(value, bool) or value is None:
        raise ParseError(f"Ingredient quantity is not numeric: {value!r}")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return as_json_number(value)
    text = str(value).strip()
    if not text:
        raise ParseError("Ingredient quantity is empty")
    try:
        return as_json_number(float(text))
    except ValueError as exc:
        raise ParseError(f"Ingredient quantity is not numeric: {value!r}") from exc


def coerce_preparations(value: Any) -> list[str]:
    """Normalize preparations to a list of non-empty strings."""
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        steps: list[str] = []
        for item in value:
            if item is None:
                continue
            if isinstance(item, Mapping):
                text = str(item.get("step") or item.get("text") or "").strip()
            else:
                text = str(item).strip()
            if text:
                steps.append(text)
        return steps
    text = str(value).strip()
    return [text] if text else []


@dataclass
class Ingredient:
    item: str
    quantity: int | float
    unit: str | None = None
    comment: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "item": self.item,
            "quantity": as_json_number(self.quantity),
        }
        if self.unit:
            data["unit"] = self.unit
        if self.comment:
            data["comment"] = self.comment
        return data


@dataclass
class Recipe:
    name: str
    ingredients: list[Ingredient] = field(default_factory=list)
    preparations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ingredients": [ingredient.to_dict() for ingredient in self.ingredients],
            "preparations": list(self.preparations),
        }


def ingredient_from_mapping(data: Any) -> Ingredient:
    if not isinstance(data, Mapping):
        raise ParseError(f"Ingredient must be a mapping, got {type(data).__name__}")
    item = str(data.get("item") or "").strip()
    if not item:
        raise ParseError("Ingredient is missing an item name")
    if "quantity" not in data or data.get("quantity") is None:
        raise ParseError(f"Ingredient {item!r} is missing a quantity")
    unit = data.get("unit")
    unit_text = str(unit).strip() if unit is not None else ""
    comment = data.get("comment")
    comment_text = str(comment).strip() if comment is not None else ""
    return Ingredient(
        item=item,
        quantity=parse_quantity(data["quantity"]),
        unit=unit_text or None,
        comment=comment_text or None,
    )


def recipe_from_mapping(data: Any) -> Recipe:
    if not isinstance(data, Mapping):
        raise ParseError(f"Recipe must be a mapping, got {type(data).__name__}")
    name = str(data.get("name") or "").strip()
    if not name:
        raise ParseError("Recipe is missing a name")
    raw_ingredients = data.get("ingredients") or []
    if not isinstance(raw_ingredients, Sequence) or isinstance(raw_ingredients, (str, bytes)):
        raise ParseError(f"Recipe {name!r} ingredients must be a list")
    return Recipe(
        name=name,
        ingredients=[ingredient_from_mapping(item) for item in raw_ingredients],
        preparations=coerce_preparations(data.get("preparations")),
    )


def recipes_from_payload(payload: Any) -> list[Recipe]:
    """Accept a single recipe mapping or a list of recipes."""
    if payload is None:
        raise ParseError("Recipe document is empty")
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        if not payload:
            raise ParseError("Recipe document contains an empty list")
        return [recipe_from_mapping(item) for item in payload]
    return [recipe_from_mapping(payload)]
