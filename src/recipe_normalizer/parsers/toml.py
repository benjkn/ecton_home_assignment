"""TOML recipe parser."""

import tomllib
from pathlib import Path

from recipe_normalizer.exceptions import ParseError
from recipe_normalizer.models import Recipe, recipes_from_payload


class TomlParser:
    def parse(self, path: Path) -> list[Recipe]:
        try:
            payload = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            raise ParseError(f"Invalid TOML: {exc}", path) from exc
        except OSError as exc:
            raise ParseError(f"Could not read file: {exc}", path) from exc
        try:
            recipes = payload.get("recipes") if isinstance(payload, dict) else None
            if recipes is not None:
                return recipes_from_payload(recipes)
            return recipes_from_payload(payload)
        except ParseError as exc:
            raise ParseError(str(exc), path) from exc
