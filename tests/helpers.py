"""Shared assertions helpers for the test suite."""

from typing import Any


def by_name(recipes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Key recipes by name so comparisons ignore array order."""
    return {recipe["name"]: recipe for recipe in recipes}
