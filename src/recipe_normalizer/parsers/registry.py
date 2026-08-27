"""Map file suffixes to parsers."""

from pathlib import Path

from recipe_normalizer.parsers.base import Parser
from recipe_normalizer.parsers.json import JsonParser
from recipe_normalizer.parsers.toml import TomlParser
from recipe_normalizer.parsers.xml import XmlParser
from recipe_normalizer.parsers.yaml import YamlParser

_PARSERS: dict[str, Parser] = {
    ".xml": XmlParser(),
    ".yaml": YamlParser(),
    ".yml": YamlParser(),
    ".json": JsonParser(),
    ".toml": TomlParser(),
}

SUPPORTED_SUFFIXES = frozenset(_PARSERS)


def parser_for(path: Path) -> Parser | None:
    return _PARSERS.get(path.suffix.lower())
