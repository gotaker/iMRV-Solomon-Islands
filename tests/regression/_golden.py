"""Golden-file load/diff/update helper for Layer 4."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

GOLDEN_DIR = Path(__file__).resolve().parent.parent / "golden"


def _path(name: str) -> Path:
    assert name.endswith(".json"), f"golden file name must end in .json: {name!r}"
    return GOLDEN_DIR / name


def assert_golden(name: str, actual: Any) -> None:
    """
    On first run (or with TESTS_UPDATE_GOLDEN=1): write `actual` to tests/golden/<name>.
    On subsequent runs: assert deep-equality against the stored snapshot.
    """
    path = _path(name)
    actual_norm = json.loads(json.dumps(actual, sort_keys=True, default=str))

    if os.environ.get("TESTS_UPDATE_GOLDEN") == "1" or not path.exists():
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(actual_norm, indent=2, sort_keys=True) + "\n")
        if not os.environ.get("TESTS_UPDATE_GOLDEN"):
            # First-write path — pass, but log so the dev knows to commit.
            print(f"[golden] wrote new snapshot: {path}")
        return

    expected = json.loads(path.read_text())
    assert actual_norm == expected, (
        f"Golden mismatch for {name}. "
        f"Run `TESTS_UPDATE_GOLDEN=1 ./tests/run.sh --layer regression` to regenerate."
    )
