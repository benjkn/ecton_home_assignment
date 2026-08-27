import pytest

from recipe_normalizer.models import Ingredient, Recipe
from recipe_normalizer.transformers.metric import MetricTransformer, convert_ingredient


@pytest.mark.parametrize(
    ("quantity", "unit", "expected_quantity", "expected_unit"),
    [
        (0.44, "pound", 200, "gr"),
        (2.02, "fl. oz.", 60, "ml"),
        (1, "gallon", 3.78, "liter"),
        (2, "cups", 480, "gr"),
        (10, "ml", 10, "ml"),
        (1, "grams", 1, "gr"),
        (2, "tbsp", 30, "ml"),
        (3, "tsp", 15, "ml"),
        (1, "oz", 28, "gr"),
        (1, "pint", 473, "ml"),
        (1, "quart", 0.95, "liter"),
        (12, None, 12, None),
    ],
)
def test_imperial_to_metric_conversions(
    quantity: float,
    unit: str | None,
    expected_quantity: float,
    expected_unit: str | None,
) -> None:
    converted = convert_ingredient(Ingredient(item="x", quantity=quantity, unit=unit))
    assert converted.quantity == expected_quantity
    assert converted.unit == expected_unit


def test_unknown_unit_is_left_unchanged() -> None:
    converted = convert_ingredient(Ingredient(item="spice", quantity=1, unit="pinch"))
    assert converted.unit == "pinch"
    assert converted.quantity == 1


def test_metric_transformer_preserves_name_and_preparations() -> None:
    recipe = Recipe(
        name="rice",
        ingredients=[Ingredient(item="rice", quantity=0.44, unit="pound")],
        preparations=["omitted for brevity"],
    )
    converted = MetricTransformer().apply(recipe)
    assert converted.name == "rice"
    assert converted.preparations == ["omitted for brevity"]
    assert converted.ingredients[0].quantity == 200
