"""Shared selftest runner used by `actor` and `sensor` packages.

Provides a single `run_selftests` function to discover Python modules in a
directory, import them in isolation and call a `selftest()` function if
available. Returns a mapping filename -> (status, payload).

This consolidates duplicated logic previously present in both
`actor/actors.py` and `sensor/sensors.py`.
"""
from __future__ import annotations

import importlib.util
import json
import traceback
import uuid
from pathlib import Path
from typing import Dict, Tuple, Optional

Result = Tuple[str, Optional[object]]


def run_selftests(directory: Optional[str] = None, pattern: str = "*.py", *, verbose: bool = False) -> Dict[str, Result]:
    base = Path(directory) if directory else Path(__file__).parent
    results: Dict[str, Result] = {}

    for path in sorted(base.glob(pattern)):
        if path.name == "__init__.py":
            continue
        # avoid importing this runner if present
        if path.resolve() == Path(__file__).resolve():
            continue

        mod_name = f"mod_{path.stem}_{uuid.uuid4().hex}"
        try:
            spec = importlib.util.spec_from_file_location(mod_name, str(path))
            module = importlib.util.module_from_spec(spec)
            assert spec is not None and spec.loader is not None
            spec.loader.exec_module(module)
        except Exception:
            tb = traceback.format_exc()
            results[path.name] = ("import_error", tb)
            if verbose:
                print(f"{path.name}: import_error\n{tb}")
            continue

        st = getattr(module, "selftest", None)
        if not callable(st):
            results[path.name] = ("no_selftest", None)
            if verbose:
                print(f"{path.name}: no_selftest")
            continue

        try:
            ret = st()
            # Ensure return value is JSON-serializable; if not, convert to repr()
            try:
                json.dumps(ret)
                payload = ret
            except Exception:
                payload = repr(ret)

            results[path.name] = ("ok", payload)
            if verbose:
                print(f"{path.name}: ok -> {payload!r}")
        except Exception:
            tb = traceback.format_exc()
            results[path.name] = ("error", tb)
            if verbose:
                print(f"{path.name}: error\n{tb}")

    return results
