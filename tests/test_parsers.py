from pathlib import Path

import pytest

from recipe_normalizer.exceptions import ParseError
from recipe_normalizer.parsers.json import JsonParser
from recipe_normalizer.parsers.toml import TomlParser
from recipe_normalizer.parsers.xml import XmlParser
from recipe_normalizer.parsers.yaml import YamlParser
from tests.paths import BROTH_JSON, PUDDING_XML, RICE_YAML, TOAST_TOML


def test_xml_parser_reads_provided_pudding_fixture() -> None:
    recipes = XmlParser().parse(PUDDING_XML)
    assert len(recipes) == 1
    pudding = recipes[0]
    assert pudding.name == "pudding"
    assert [ing.item for ing in pudding.ingredients] == ["milk", "sugar", "vanilla", "egg yolks"]
    assert pudding.ingredients[0].unit == "gallon"
    assert pudding.ingredients[3].unit is None
    assert pudding.ingredients[3].comment == "room temperature"
    assert pudding.preparations == ["omitted for brevity"]


def test_yaml_parser_reads_provided_rice_fixture() -> None:
    recipes = YamlParser().parse(RICE_YAML)
    assert len(recipes) == 1
    rice = recipes[0]
    assert rice.name == "rice"
    assert rice.ingredients[0].quantity == 0.44
    assert rice.ingredients[0].unit == "pound"
    assert rice.ingredients[1].unit == "fl. oz."
    assert rice.ingredients[2].comment == "white or red"
    assert rice.ingredients[2].unit is None


def test_json_parser_reads_single_recipe() -> None:
    recipes = JsonParser().parse(BROTH_JSON)
    assert recipes[0].name == "broth"
    assert recipes[0].ingredients[1].unit == "tsp"


def test_toml_parser_reads_array_of_tables() -> None:
    recipes = TomlParser().parse(TOAST_TOML)
    assert recipes[0].name == "toast"
    assert recipes[0].ingredients[1].unit == "tbsp"
    assert recipes[0].preparations == ["toast until golden"]


def test_xml_parser_supports_recipe_collection(tmp_path: Path) -> None:
    path = tmp_path / "batch.xml"
    path.write_text(
        """
        <recipes>
          <recipe><name>a</name><ingredients><item>x</item><quantity>1</quantity></ingredients></recipe>
          <recipe><name>b</name><ingredients><item>y</item><quantity>2</quantity></ingredients></recipe>
        </recipes>
        """,
        encoding="utf-8",
    )
    names = [recipe.name for recipe in XmlParser().parse(path)]
    assert names == ["a", "b"]


def test_invalid_xml_raises_parse_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.xml"
    path.write_text("<root><unclosed>", encoding="utf-8")
    with pytest.raises(ParseError, match="Invalid XML"):
        XmlParser().parse(path)


def test_invalid_yaml_raises_parse_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("name: [unterminated", encoding="utf-8")
    with pytest.raises(ParseError, match="Invalid YAML"):
        YamlParser().parse(path)
