"""Utility to run self-tests for all sensor modules.

This module dynamically imports all Python files in the sensors directory
and executes their selftest() function if available.
"""
import traceback
import uuid
from pathlib import Path
import json
import importlib.util


def run_selftests(directory: str = None, pattern: str = "*.py", *, verbose: bool = False):
    """
    Import every Python file in `directory` (defaults to this file's dir),
    call its `selftest()` if present, and return a dict of results.

    Result format: { filename: ("ok", return_value) |
                             ("no_selftest", None) |
                             ("import_error", traceback_str) |
                             ("error", traceback_str) }
    """
    base = Path(directory) if directory else Path(__file__).parent
    results = {}

    for path in base.glob(pattern):
        if path.name == "__init__.py":
            continue
        if path.resolve() == Path(__file__).resolve():
            continue

        mod_name = f"actors_{path.stem}_{uuid.uuid4().hex}"
        try:
            spec = importlib.util.spec_from_file_location(mod_name, str(path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception:
            results[path.name] = ("import_error", traceback.format_exc())
            if verbose:
                print(f"{path.name}: import_error\n{results[path.name][1]}")
            continue

        st = getattr(module, "selftest", None)
        if not callable(st):
            results[path.name] = ("no_selftest", None)
            if verbose:
                print(f"{path.name}: no_selftest")
            continue

        try:
            ret = st()
            results[path.name] = ("ok", ret)
            if verbose:
                print(f"{path.name}: ok -> {ret!r}")
        except Exception:
            results[path.name] = ("error", traceback.format_exc())
            if verbose:
                print(f"{path.name}: error\n{results[path.name][1]}")

    return results


if __name__ == "__main__":
    # quick CLI runner
    res = run_selftests(verbose=True)
    print("\nSummary:")
    print(json.dumps(res, indent=2))