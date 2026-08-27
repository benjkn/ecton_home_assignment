"""Convert imperial cooking units to metric units."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Final

from recipe_normalizer.models import Ingredient, Recipe, as_json_number


@dataclass(frozen=True)
class Conversion:
    target_unit: str
    factor: float
    decimal_places: int


def _key(unit: str) -> str:
    cleaned = unit.strip().lower().replace(".", " ").replace("-", " ")
    return " ".join(cleaned.split())


# Canonical metric names used in output.
METRIC_ALIASES: Final[dict[str, str]] = {
    "g": "gr",
    "gr": "gr",
    "gram": "gr",
    "grams": "gr",
    "ml": "ml",
    "milliliter": "ml",
    "millilitre": "ml",
    "milliliters": "ml",
    "millilitres": "ml",
    "l": "liter",
    "liter": "liter",
    "litre": "liter",
    "liters": "liter",
    "litres": "liter",
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
}

# Imperial (and cooking) units → metric. Factors match the supplied fixtures
# for pound, gallon, fl. oz., and cup; remaining entries are standard cooking
# approximations documented in README.md.
IMPERIAL_CONVERSIONS: Final[dict[str, Conversion]] = {
    "pound": Conversion("gr", 453.59237, 0),
    "pounds": Conversion("gr", 453.59237, 0),
    "lb": Conversion("gr", 453.59237, 0),
    "lbs": Conversion("gr", 453.59237, 0),
    "ounce": Conversion("gr", 28.349523125, 0),
    "ounces": Conversion("gr", 28.349523125, 0),
    "oz": Conversion("gr", 28.349523125, 0),
    "gallon": Conversion("liter", 3.78, 2),
    "gallons": Conversion("liter", 3.78, 2),
    "gal": Conversion("liter", 3.78, 2),
    "quart": Conversion("liter", 0.95, 2),
    "quarts": Conversion("liter", 0.95, 2),
    "qt": Conversion("liter", 0.95, 2),
    "pint": Conversion("ml", 473, 0),
    "pints": Conversion("ml", 473, 0),
    "pt": Conversion("ml", 473, 0),
    "cup": Conversion("gr", 240, 0),
    "cups": Conversion("gr", 240, 0),
    "fl oz": Conversion("ml", 29.5735295625, 0),
    "fluid ounce": Conversion("ml", 29.5735295625, 0),
    "fluid ounces": Conversion("ml", 29.5735295625, 0),
    "floz": Conversion("ml", 29.5735295625, 0),
    "tablespoon": Conversion("ml", 15, 0),
    "tablespoons": Conversion("ml", 15, 0),
    "tbsp": Conversion("ml", 15, 0),
    "tbs": Conversion("ml", 15, 0),
    "teaspoon": Conversion("ml", 5, 0),
    "teaspoons": Conversion("ml", 5, 0),
    "tsp": Conversion("ml", 5, 0),
}


def convert_quantity(quantity: int | float, conversion: Conversion) -> int | float:
    raw = float(quantity) * conversion.factor
    rounded = round(raw, conversion.decimal_places)
    return as_json_number(rounded)


def convert_unit(unit: str | None) -> tuple[str | None, Conversion | None]:
    """Return (canonical unit, conversion-to-apply-or-None)."""
    if not unit:
        return None, None
    key = _key(unit)
    if key in IMPERIAL_CONVERSIONS:
        conversion = IMPERIAL_CONVERSIONS[key]
        return conversion.target_unit, conversion
    if key in METRIC_ALIASES:
        return METRIC_ALIASES[key], None
    return unit, None


def convert_ingredient(ingredient: Ingredient) -> Ingredient:
    canonical, conversion = convert_unit(ingredient.unit)
    if conversion is None:
        return replace(ingredient, unit=canonical)
    return replace(
        ingredient,
        quantity=convert_quantity(ingredient.quantity, conversion),
        unit=canonical,
    )


class MetricTransformer:
    name = "metric"

    def apply(self, recipe: Recipe) -> Recipe:
        return replace(
            recipe,
            ingredients=[convert_ingredient(item) for item in recipe.ingredients],
            preparations=list(recipe.preparations),
        )
