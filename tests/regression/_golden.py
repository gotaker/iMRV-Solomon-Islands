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
    Snapshot assert with three modes:

    1. TESTS_UPDATE_GOLDEN=1 set → overwrite existing snapshot silently, pass.
    2. Snapshot file missing AND no env var → write, then FAIL the test with a
       clear message so the developer inspects the file before trusting it.
       This prevents "silently green on first run" — the whole point of a
       snapshot is that a human has signed off on the expected shape.
    3. Snapshot file exists AND no env var → compare for deep equality.
    """
    import pytest

    path = _path(name)
    actual_norm = json.loads(json.dumps(actual, sort_keys=True, default=str))

    if os.environ.get("TESTS_UPDATE_GOLDEN") == "1":
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(actual_norm, indent=2, sort_keys=True) + "\n")
        return

    if not path.exists():
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(actual_norm, indent=2, sort_keys=True) + "\n")
        pytest.fail(
            f"[golden] wrote NEW snapshot {path} — INSPECT it and commit, then "
            f"re-run to confirm. First-run writes are not auto-trusted."
        )

    expected = json.loads(path.read_text())
    assert actual_norm == expected, (
        f"Golden mismatch for {name}. "
        f"Run `TESTS_UPDATE_GOLDEN=1 ./tests/run.sh --layer regression` to regenerate."
    )
