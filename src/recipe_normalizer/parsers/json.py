"""JSON recipe parser."""

import json
from pathlib import Path

from recipe_normalizer.exceptions import ParseError
from recipe_normalizer.models import Recipe, recipes_from_payload


class JsonParser:
    def parse(self, path: Path) -> list[Recipe]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ParseError(f"Invalid JSON: {exc}", path) from exc
        except OSError as exc:
            raise ParseError(f"Could not read file: {exc}", path) from exc
        try:
            return recipes_from_payload(payload)
        except ParseError as exc:
            raise ParseError(str(exc), path) from exc
