"""Orchestrate discovery, parsing, transformation, and serialization."""

from __future__ import annotations

import logging
from pathlib import Path

from recipe_normalizer.discovery import discover_recipe_files
from recipe_normalizer.exceptions import ParseError, RecipeNormalizerError
from recipe_normalizer.models import Recipe
from recipe_normalizer.parsers import parser_for
from recipe_normalizer.transformers import get_transformer

logger = logging.getLogger(__name__)


def load_recipes(input_dir: Path, *, recursive: bool = False) -> list[Recipe]:
    files = discover_recipe_files(input_dir, recursive=recursive)
    if not files:
        logger.warning("No supported recipe files found in %s", input_dir)
        return []

    recipes: list[Recipe] = []
    for path in files:
        parser = parser_for(path)
        if parser is None:
            continue
        try:
            parsed = parser.parse(path)
        except ParseError as exc:
            logger.error("Skipping %s: %s", path.name, exc)
            continue
        except OSError as exc:
            logger.error("Skipping %s: %s", path.name, exc)
            continue
        logger.info("Parsed %s recipe(s) from %s", len(parsed), path.name)
        recipes.extend(parsed)
    return recipes


def normalize_recipes(
    recipes: list[Recipe],
    *,
    transform: str = "metric",
) -> list[Recipe]:
    transformer = get_transformer(transform)
    return [transformer.apply(recipe) for recipe in recipes]


def run(
    input_dir: Path,
    *,
    transform: str = "metric",
    recursive: bool = False,
) -> list[Recipe]:
    recipes = load_recipes(input_dir, recursive=recursive)
    if not recipes:
        raise RecipeNormalizerError(f"No recipes could be loaded from {input_dir}")
    return normalize_recipes(recipes, transform=transform)
