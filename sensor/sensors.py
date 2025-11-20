"""Sensor selftest CLI wrapper.

Thin wrapper around `utils.selftest.run_selftests` to expose a simple CLI for
testing sensors in the repository.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from utils.selftest import run_selftests


def run_sensor_selftests(directory: Optional[str] = None, pattern: str = "*.py", *, verbose: bool = False):
    base = Path(directory) if directory else Path(__file__).parent
    return run_selftests(str(base), pattern, verbose=verbose)


if __name__ == "__main__":
    res = run_sensor_selftests(verbose=True)
    print("\nSummary:")
    import json

    print(json.dumps(res, indent=2))