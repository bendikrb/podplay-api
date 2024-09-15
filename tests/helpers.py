from __future__ import annotations

from pathlib import Path
import re

import orjson

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def save_fixture(name: str, data: dict):
    """Save API response data to a fixture file."""
    file_path = FIXTURE_DIR / f"{name}.json"
    with open(file_path, "w") as f:
        f.write(orjson.dumps(data))


def load_fixture(name: str) -> str:
    """Load a fixture."""
    path = FIXTURE_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Fixture {name} not found")
    return path.read_text(encoding="utf-8")


def load_fixture_json(name: str) -> dict:
    """Load a fixture as JSON."""
    data = load_fixture(name)
    return orjson.loads(data)


def build_path_pattern(uri: str) -> re.Pattern:
    """Build a URL path pattern."""
    return re.compile(rf"/v1(?:/(?:no|sv|fi|en))?/{uri}")
