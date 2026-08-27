import pytest

from recipe_normalizer.exceptions import ParseError
from recipe_normalizer.models import (
    as_json_number,
    coerce_preparations,
    ingredient_from_mapping,
    recipe_from_mapping,
    recipes_from_payload,
)


def test_as_json_number_converts_whole_floats() -> None:
    assert as_json_number(200.0) == 200
    assert as_json_number(3.78) == 3.78
    assert isinstance(as_json_number(200.0), int)


def test_ingredient_omits_empty_optional_fields() -> None:
    ingredient = ingredient_from_mapping({"item": "onion", "quantity": 1, "unit": "", "comment": "white or red"})
    assert ingredient.to_dict() == {"item": "onion", "quantity": 1, "comment": "white or red"}


def test_ingredient_requires_item_and_quantity() -> None:
    with pytest.raises(ParseError, match="item name"):
        ingredient_from_mapping({"quantity": 1})
    with pytest.raises(ParseError, match="quantity"):
        ingredient_from_mapping({"item": "salt"})


def test_recipe_from_mapping_normalizes_string_preparations() -> None:
    recipe = recipe_from_mapping(
        {
            "name": "pudding",
            "ingredients": [{"item": "milk", "quantity": 1, "unit": "gallon"}],
            "preparations": "omitted for brevity",
        }
    )
    assert recipe.preparations == ["omitted for brevity"]


def test_recipes_from_payload_accepts_list() -> None:
    recipes = recipes_from_payload(
        [
            {"name": "a", "ingredients": [{"item": "x", "quantity": 1}]},
            {"name": "b", "ingredients": [{"item": "y", "quantity": 2}]},
        ]
    )
    assert [recipe.name for recipe in recipes] == ["a", "b"]


def test_coerce_preparations_filters_empty() -> None:
    assert coerce_preparations(None) == []
    assert coerce_preparations(["a", "  ", None, {"step": "b"}]) == ["a", "b"]


def test_missing_recipe_name_is_an_error() -> None:
    with pytest.raises(ParseError, match="missing a name"):
        recipe_from_mapping({"ingredients": []})
