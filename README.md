# Recipe Normalizer

CLI that reads cooking recipes from a directory (XML, YAML, JSON, TOML), converts imperial units to metric, and writes one JSON file.

## Run

Python 3.12+ required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

```bash
recipe-normalizer examples/ -o recipes.json
python -m recipe_normalizer examples/ -o recipes.json
```

Omit `-o` to print JSON to stdout. `examples/broken.yaml` is intentionally invalid; it is logged and skipped, and the valid recipes are still written.

```text
usage: recipe-normalizer [-h] [-o OUTPUT] [--transform {metric,none}]
                         [-r] [-v]
                         input_dir
```

`--transform metric` is the default (pound → gr, fl. oz. → ml, gallon → liter, cups → gr). Use `--transform none` to parse without converting units. `-r` scans subdirectories.

```bash
pytest
```

```bash
docker build -t recipe-normalizer .
docker run --rm -v "$(pwd)/examples:/data:ro" recipe-normalizer /data
```

## Architecture

Parsers (by file suffix), a shared `Recipe` model, and a pluggable metric transformer sit behind one pipeline: discover → parse → transform → write JSON. Adding a format or a transform is a registry entry, not a change to the CLI.

We reproduce the provided sample output (rice + pudding), skip unreadable files instead of failing the whole run, and ship unit tests plus a Dockerfile.

## Assumptions

- **In-memory.** All recipes are loaded, then written as one JSON document. Peak RAM is several times the output size. Fine for a normal folder; a huge corpus could OOM.
- **Order.** Recipes are emitted in filename order (stable). The sample lists rice before pudding; we did not special-case that.
- **Formats.** XML, YAML, JSON, TOML, by file extension, UTF-8. Other extensions are ignored. A file may hold one recipe or a list (XML: a `<recipes>` collection).
- **Input.** A directory, not a single file. Non-recursive unless `-r`. Hidden files (`.…`) are ignored.
- **Schema.** `item` and `quantity` are required. `unit` and `comment` are omitted when absent. Empty `<unit></unit>` means no unit. Whole numbers serialize as integers.
- **Preparations.** Always a list of strings. No serving-size scaling, and no unit/temperature conversion inside preparation text.
- **Units.** US customary. Factors follow the sample, not exact SI: 1 gallon = 3.78 liter, 1 cup = 240 gr (water density, so 2 cups sugar → 480 gr). Bare `oz` is weight; fluid ounces must be `fl oz`. Unknown units pass through; one WARNING per recipe.
- **Errors.** A bad file is logged and skipped. Exit non-zero only if nothing could be loaded. No `-o` → stdout.
- **Rerun.** The same `-o` path is **overwritten**. A second file is not created.
- **Duplicates.** There is **no deduplication**. Two files with the same recipe (or the same name) both appear in the output. If the output JSON is written back into the input directory, a later run will parse it as extra recipes and append them.

## Original requirements

### Objective

Develop a command-line application that normalizes cooking recipes from various input formats (like XML, YAML, among few others) to a consistent JSON file format.

The application should read all recipes in a given directory.

The application should be able to run transformations on recipes, for example:

* convert imperial units to metric units (like pound → grams, fl. oz. → ml, etc...)

The output is a single JSON file with all the parsed recipes.