"""Convert imperial cooking units to metric units."""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from typing import Final

from recipe_normalizer.models import Ingredient, Recipe, as_json_number

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Conversion:
    target_unit: str
    factor: float


def _normalize(unit: str) -> str:
    cleaned = unit.strip().lower().replace(".", " ").replace("-", " ")
    return " ".join(cleaned.split())


# Accepted spellings grouped under the canonical unit name they resolve to.
_ALIAS_GROUPS: Final[dict[str, tuple[str, ...]]] = {
    "gr": ("g", "gr", "gram", "grams"),
    "ml": ("ml", "milliliter", "milliliters", "millilitre", "millilitres"),
    "liter": ("l", "liter", "liters", "litre", "litres"),
    "kg": ("kg", "kilogram", "kilograms"),
    "pound": ("pound", "pounds", "lb", "lbs"),
    # Bare "oz" resolves to weight; fluid ounces must be spelled "fl oz".
    "ounce": ("ounce", "ounces", "oz"),
    "gallon": ("gallon", "gallons", "gal"),
    "quart": ("quart", "quarts", "qt"),
    "pint": ("pint", "pints", "pt"),
    "cup": ("cup", "cups"),
    "fluid ounce": ("fl oz", "floz", "fluid ounce", "fluid ounces"),
    "tablespoon": ("tablespoon", "tablespoons", "tbsp", "tbs"),
    "teaspoon": ("teaspoon", "teaspoons", "tsp"),
}

_CANONICAL_UNITS: Final[dict[str, str]] = {
    alias: canonical
    for canonical, aliases in _ALIAS_GROUPS.items()
    for alias in aliases
}

# Gallon and cup use the factors implied by the provided sample output
# (3.78 l/gal, 240 g/cup at water density) rather than exact SI values.
_CONVERSIONS: Final[dict[str, Conversion]] = {
    "pound": Conversion("gr", 453.59237),
    "ounce": Conversion("gr", 28.349523125),
    "gallon": Conversion("liter", 3.78),
    "quart": Conversion("liter", 0.95),
    "pint": Conversion("ml", 473),
    "cup": Conversion("gr", 240),
    "fluid ounce": Conversion("ml", 29.5735295625),
    "tablespoon": Conversion("ml", 15),
    "teaspoon": Conversion("ml", 5),
}

# Rounding belongs to the unit a quantity is reported in, not to the conversion.
_DECIMAL_PLACES: Final[dict[str, int]] = {"gr": 0, "ml": 0, "liter": 2}
_DEFAULT_DECIMAL_PLACES: Final[int] = 2


def canonical_unit(unit: str) -> str | None:
    """Return the canonical name for ``unit``, or None if it is unrecognized."""
    return _CANONICAL_UNITS.get(_normalize(unit))


def convert_quantity(quantity: int | float, conversion: Conversion) -> int | float:
    places = _DECIMAL_PLACES.get(conversion.target_unit, _DEFAULT_DECIMAL_PLACES)
    return as_json_number(round(float(quantity) * conversion.factor, places))


def convert_unit(unit: str | None) -> tuple[str | None, Conversion | None]:
    """Return the unit to report in and the conversion to apply, if any."""
    if not unit:
        return None, None
    canonical = canonical_unit(unit)
    if canonical is None:
        return unit, None
    conversion = _CONVERSIONS.get(canonical)
    if conversion is None:
        return canonical, None
    return conversion.target_unit, conversion


def convert_ingredient(ingredient: Ingredient) -> Ingredient:
    target_unit, conversion = convert_unit(ingredient.unit)
    if conversion is None:
        return replace(ingredient, unit=target_unit)
    return replace(
        ingredient,
        quantity=convert_quantity(ingredient.quantity, conversion),
        unit=target_unit,
    )


def unrecognized_units(recipe: Recipe) -> list[str]:
    return sorted(
        {
            ingredient.unit
            for ingredient in recipe.ingredients
            if ingredient.unit and canonical_unit(ingredient.unit) is None
        }
    )


class MetricTransformer:
    name = "metric"

    def apply(self, recipe: Recipe) -> Recipe:
        unknown = unrecognized_units(recipe)
        if unknown:
            logger.warning(
                "Recipe %r: no conversion for unit(s) %s; left unchanged",
                recipe.name,
                ", ".join(repr(unit) for unit in unknown),
            )
        return replace(
            recipe,
            ingredients=[convert_ingredient(item) for item in recipe.ingredients],
            preparations=list(recipe.preparations),
        )
