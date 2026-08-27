import json
import logging
from pathlib import Path

from recipe_normalizer.cli import main
from tests.helpers import by_name
from tests.paths import EXPECTED_OUTPUT, FIXTURES


def test_cli_examples_skips_broken_file(tmp_path: Path, caplog) -> None:
    examples = Path(__file__).resolve().parents[1] / "examples"
    output = tmp_path / "recipes.json"
    with caplog.at_level(logging.ERROR):
        assert main([str(examples), "-o", str(output)]) == 0
    assert any("Skipping broken.yaml" in record.getMessage() for record in caplog.records)
    assert by_name(json.loads(output.read_text(encoding="utf-8"))) == by_name(
        json.loads(EXPECTED_OUTPUT.read_text(encoding="utf-8"))
    )


def test_cli_writes_expected_output(tmp_path: Path) -> None:
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    (input_dir / "pudding.xml").write_text((FIXTURES / "pudding.xml").read_text(encoding="utf-8"), encoding="utf-8")
    (input_dir / "rice.yaml").write_text((FIXTURES / "rice.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    output = tmp_path / "out" / "recipes.json"

    assert main([str(input_dir), "-o", str(output)]) == 0
    assert by_name(json.loads(output.read_text(encoding="utf-8"))) == by_name(
        json.loads(EXPECTED_OUTPUT.read_text(encoding="utf-8"))
    )


def test_cli_stdout(tmp_path: Path, capsys) -> None:
    (tmp_path / "a.yaml").write_text(
        "name: tea\ningredients:\n- item: water\n  quantity: 1\n  unit: cup\n",
        encoding="utf-8",
    )
    assert main([str(tmp_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["ingredients"][0] == {"item": "water", "quantity": 240, "unit": "gr"}


def test_cli_missing_directory_returns_2(tmp_path: Path) -> None:
    assert main([str(tmp_path / "missing")]) == 2


def test_cli_empty_directory_returns_1(tmp_path: Path) -> None:
    assert main([str(tmp_path)]) == 1


def test_cli_none_transform_keeps_imperial(tmp_path: Path, capsys) -> None:
    (tmp_path / "a.yaml").write_text(
        "name: tea\ningredients:\n- item: water\n  quantity: 1\n  unit: cup\n",
        encoding="utf-8",
    )
    assert main([str(tmp_path), "--transform", "none"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["ingredients"][0]["unit"] == "cup"
    assert payload[0]["ingredients"][0]["quantity"] == 1
