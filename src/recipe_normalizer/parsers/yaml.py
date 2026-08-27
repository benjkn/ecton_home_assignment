"""YAML recipe parser."""

from pathlib import Path

import yaml

from recipe_normalizer.exceptions import ParseError
from recipe_normalizer.models import Recipe, recipes_from_payload


class YamlParser:
    def parse(self, path: Path) -> list[Recipe]:
        try:
            text = path.read_text(encoding="utf-8")
            payload = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ParseError(f"Invalid YAML: {exc}", path) from exc
        except OSError as exc:
            raise ParseError(f"Could not read file: {exc}", path) from exc
        try:
            return recipes_from_payload(payload)
        except ParseError as exc:
            raise ParseError(str(exc), path) from exc
