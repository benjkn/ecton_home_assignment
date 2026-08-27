import json
import logging
from pathlib import Path

import pytest

from recipe_normalizer.discovery import discover_recipe_files
from recipe_normalizer.exceptions import RecipeNormalizerError
from recipe_normalizer.pipeline import run
from recipe_normalizer.writers import recipes_to_json
from tests.paths import EXPECTED_OUTPUT, FIXTURES

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_discover_non_recursive_skips_unknown_and_hidden(tmp_path: Path) -> None:
    (tmp_path / "a.yaml").write_text("name: a\ningredients: []\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / ".secret.yaml").write_text("name: hidden\ningredients: []\n", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "b.xml").write_text("<root><name>b</name></root>", encoding="utf-8")

    found = discover_recipe_files(tmp_path)
    assert [path.name for path in found] == ["a.yaml"]

    recursive = discover_recipe_files(tmp_path, recursive=True)
    assert sorted(path.name for path in recursive) == ["a.yaml", "b.xml"]


def test_examples_directory_matches_expected_output() -> None:
    recipes = run(EXAMPLES, transform="metric")
    expected_text = EXPECTED_OUTPUT.read_text(encoding="utf-8")
    expected = json.loads(expected_text)
    assert [recipe.to_dict() for recipe in recipes] == expected
    assert recipes_to_json(recipes) == expected_text


def test_examples_skips_broken_yaml_and_keeps_valid_recipes(caplog: pytest.LogCaptureFixture) -> None:
    broken = EXAMPLES / "broken.yaml"
    assert broken.exists()
    with caplog.at_level(logging.ERROR):
        recipes = run(EXAMPLES, transform="metric")
    assert any("broken.yaml" in record.getMessage() for record in caplog.records)
    assert any("Skipping" in record.getMessage() for record in caplog.records)
    assert [recipe.name for recipe in recipes] == ["rice", "pudding"]


def test_pipeline_example_directory(tmp_path: Path) -> None:
    (tmp_path / "pudding.xml").write_text((FIXTURES / "pudding.xml").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "rice.yaml").write_text((FIXTURES / "rice.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    recipes = run(tmp_path, transform="metric")
    expected = json.loads(EXPECTED_OUTPUT.read_text(encoding="utf-8"))
    assert [recipe.to_dict() for recipe in recipes] == expected
    assert json.loads(recipes_to_json(recipes)) == expected


def test_pipeline_keeps_stable_file_order(tmp_path: Path) -> None:
    (tmp_path / "z.yaml").write_text("name: zucchini\ningredients:\n- item: z\n  quantity: 1\n", encoding="utf-8")
    (tmp_path / "a.yaml").write_text("name: apple\ningredients:\n- item: a\n  quantity: 1\n", encoding="utf-8")
    (tmp_path / "b.xml").write_text(
        "<root><name>beet</name><ingredients><item>b</item><quantity>1</quantity></ingredients></root>",
        encoding="utf-8",
    )
    recipes = run(tmp_path, transform="none")
    assert [recipe.name for recipe in recipes] == ["apple", "zucchini", "beet"]


def test_pipeline_errors_when_no_recipes(tmp_path: Path) -> None:
    (tmp_path / "readme.txt").write_text("nothing", encoding="utf-8")
    with pytest.raises(RecipeNormalizerError, match="No recipes"):
        run(tmp_path)


def test_pipeline_loads_all_supported_fixture_formats() -> None:
    recipes = run(FIXTURES, transform="metric")
    assert [recipe.name for recipe in recipes] == ["rice", "pudding", "broth", "toast"]
    toast = next(recipe for recipe in recipes if recipe.name == "toast")
    assert toast.ingredients[1].unit == "ml"
    assert toast.ingredients[1].quantity == 15


def test_skips_unreadable_file_and_loads_the_rest(tmp_path: Path) -> None:
    (tmp_path / "good.yaml").write_text("name: ok\ningredients:\n- item: x\n  quantity: 1\n", encoding="utf-8")
    (tmp_path / "bad.xml").write_text("<not-xml", encoding="utf-8")
    recipes = run(tmp_path, transform="none")
    assert [recipe.name for recipe in recipes] == ["ok"]
