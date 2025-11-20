"""Actor selftest CLI wrapper.

This module is a thin wrapper around `utils.selftest.run_selftests` so that
the actor package continues to expose a convenient CLI entrypoint. The
actual discovery and execution logic lives in `utils/selftest.py` to avoid
duplication with the sensors package.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from utils.selftest import run_selftests


def run_actor_selftests(
        directory: Optional[str] = None,
        pattern: str = "*.py",
        *,
        verbose: bool = False):
    base = Path(directory) if directory else Path(__file__).parent
    return run_selftests(str(base), pattern, verbose=verbose)


if __name__ == "__main__":
    # quick CLI runner
    res = run_actor_selftests(verbose=True)
    print("\nSummary:")
    import json

    print(json.dumps(res, indent=2))
