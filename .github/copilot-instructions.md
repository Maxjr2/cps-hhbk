<!-- Copilot / AI agent instructions for the cps-hhbk repository -->

# Quick orientation

This repository implements a small temperature-monitoring control app with two clear layers:

- **Sensors**: code under `sensor/` reads hardware (1-Wire temperature sensor). Key file: `sensor/ky001.py`.
- **Actors**: code under `actor/` controls outputs (three LEDs + KY-006 buzzer). Key files: `actor/led.py`, `actor/ky006.py`.
- **Orchestration & config**: `main.py` drives behavior using values in `config.py` (thresholds and pin mappings).

All hardware access uses conditional imports (try/except) to provide mock implementations on non-RPi systems — tests and local development should rely on these mocks.

**Python / CI**: GitHub Actions sets up Python 3.10 and runs `flake8` + `pytest` (see `.github/workflows/python-app.yml`). Use the same locally.

**How to run quick checks**

- Run all linting & tests locally (same as CI):

  - `python -m pip install --upgrade pip`
  - `pip install flake8 pytest`
  - `flake8 .`
  - `pytest`

- Run the actors' self-tests from the CLI: `python -m actor.actors` (prints per-module results).
- Run the sensors' self-tests from the CLI: `python -m sensor.sensors`.
- Exercise the main logic in REPL or a small runner by importing `main` and calling `main.get_sensor_state()` or `main.run_selftests()`.

**Important files to inspect when changing behavior**

- `config.py`: central place for GPIO pin numbers, buzzer frequency and temperature thresholds (`TEMP_COLD`, `TEMP_WARM`, `TEMP_HOT`, `TEMP_CRITICAL`). Change thresholds here.
- `main.py`: maps temperature ranges -> LED color and triggers the buzzer at or above `TEMP_CRITICAL`.
- `sensor/ky001.py`: contains `MOCK_MODE` detection and `read_temp()`; it implements a CRC check loop and returns `(celsius, fahrenheit)`.
- `actor/led.py` and `actor/ky006.py`: try to import `gpiozero` and fall back to concise mock classes that print actions — rely on these for non-RPi development.
- `actor/actors.py` and `sensor/sensors.py`: dynamic selftest runners using `importlib.util.spec_from_file_location` and a consistent return format (see below).

**Selftest runner conventions**

- Both `actor/actors.py` and `sensor/sensors.py` return results as a dict mapping filename -> tuple, where tuple is one of:
  - `("ok", return_value)` — selftest succeeded
  - `("no_selftest", None)` — module had no `selftest()` function
  - `("import_error", traceback_str)` — import failed
  - `("error", traceback_str)` — `selftest()` raised

- When adding new modules, provide a `selftest()` function returning a small, JSON-serializable value (or `None`) to integrate with these runners.

**Hardware and mocking notes**

- `sensor/ky001.py` sets `MOCK_MODE = True` if the 1-Wire device path is not found. In that case `read_temp()` returns a fixed mock value (23.5°C). Use this when running on development machines.
- Actor modules define `LEDS` and `buzzer` objects at import time. Their mock classes print to stdout — tests and local debugging should assert on printed output or call methods directly.

**Coding patterns to follow**

- Prefer centralizing hardware pins and thresholds in `config.py` rather than scattering values across modules.
- Keep `selftest()` functions simple and side-effect-limited (print + return status). This ensures the dynamic import runners can call them safely.
- Use the existing try/except import pattern for any additional hardware modules so local runs remain possible.

**Common pitfalls**

- Do not assume presence of real hardware in CI or developer machines — rely on mock paths and classes.
- When parsing sensor output, `sensor/ky001.py` expects a `t=` prefix and performs a CRC check; avoid changing that behavior without updating callers.

**Examples**

- To change the critical temperature where the buzzer starts, edit `config.py` and modify `TEMP_CRITICAL` (e.g. `TEMP_CRITICAL = 35`).
- To add a new actor, add `actor/mydevice.py` with a `selftest()` and use the `actor/actors.py` runner to exercise it.

If anything here is unclear or you want more examples (unit test examples, richer mock classes, or CI test matrix changes), let me know which part to expand.
