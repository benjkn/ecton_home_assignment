"""Command-line interface for the recipe normalizer."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from recipe_normalizer.exceptions import RecipeNormalizerError
from recipe_normalizer.pipeline import run
from recipe_normalizer.transformers import AVAILABLE_TRANSFORMS
from recipe_normalizer.writers import write_recipes

logger = logging.getLogger("recipe_normalizer")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recipe-normalizer",
        description="Normalize cooking recipes from mixed formats into one JSON file.",
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing recipe files (XML, YAML, JSON, TOML).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output JSON path. Defaults to stdout.",
    )
    parser.add_argument(
        "--transform",
        choices=AVAILABLE_TRANSFORMS,
        default="metric",
        help="Transformation to apply after parsing (default: metric).",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Scan input_dir recursively.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    try:
        recipes = run(
            args.input_dir,
            transform=args.transform,
            recursive=args.recursive,
        )
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 2
    except NotADirectoryError as exc:
        logger.error("%s", exc)
        return 2
    except RecipeNormalizerError as exc:
        logger.error("%s", exc)
        return 1

    if args.output is not None:
        write_recipes(recipes, args.output)
        logger.info("Wrote %s recipe(s) to %s", len(recipes), args.output)
    else:
        write_recipes(recipes, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
