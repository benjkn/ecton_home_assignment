from pathlib import Path

ROOT = Path(__file__).parent
FIXTURES = ROOT / "fixtures"
EXPECTED_OUTPUT = ROOT / "expected" / "expected_output.json"
PUDDING_XML = FIXTURES / "pudding.xml"
RICE_YAML = FIXTURES / "rice.yaml"
TOAST_TOML = FIXTURES / "toast.toml"
BROTH_JSON = FIXTURES / "broth.json"
