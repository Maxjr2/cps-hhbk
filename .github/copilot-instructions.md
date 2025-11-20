<!-- Copilot / AI agent instructions for the cps-hhbk repository -->

# Quick orientation

This repository implements a small temperature-monitoring control app with two clear layers:

- **Sensors**: code under `sensor/` reads hardware (1-Wire temperature sensor). Key file: `sensor/ky001.py`.
- **Actors**: code under `actor/` controls outputs (three LEDs + KY-006 buzzer). Key files: `actor/led.py`, `actor/ky006.py`.
- **Orchestration & config**: `main.py` drives behavior using values in `config.py` (thresholds and pin mappings).
- **Mocking infrastructure**: `utils/mocking.py` provides centralized mock implementations for development and testing.

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
- `main.py`: contains business logic functions `determine_led_color()` and `should_activate_buzzer()` that map temperature ranges to control actions. The `get_sensor_state()` function orchestrates sensor reading and actor control.
- `utils/mocking.py`: centralized mock implementations (`MockLED`, `MockPWMOutputDevice`, `MockTemperatureSensor`) used when hardware is not available.
- `sensor/ky001.py`: detects `MOCK_MODE` and uses centralized `MockTemperatureSensor`; implements CRC check loop and returns `(celsius, fahrenheit)`. Provides `set_mock_temperature()` for testing.
- `actor/led.py` and `actor/ky006.py`: use centralized mocks from `utils.mocking` when `gpiozero` is not available.
- `actor/actors.py` and `sensor/sensors.py`: dynamic selftest runners using `utils.selftest.run_selftests` with consistent return format.
- `tests/test_logic.py`: comprehensive logic-based tests that validate business behavior rather than implementation details.

**Selftest runner conventions**

- Both `actor/actors.py` and `sensor/sensors.py` return results as a dict mapping filename -> tuple, where tuple is one of:
  - `("ok", return_value)` — selftest succeeded
  - `("no_selftest", None)` — module had no `selftest()` function
  - `("import_error", traceback_str)` — import failed
  - `("error", traceback_str)` — `selftest()` raised

- When adding new modules, provide a `selftest()` function returning a small, JSON-serializable value (or `None`) to integrate with these runners.

**Hardware and mocking notes**

- `sensor/ky001.py` sets `MOCK_MODE = True` if the 1-Wire device path is not found. It uses the centralized `MockTemperatureSensor` from `utils.mocking` which provides configurable temperature readings via `set_mock_temperature()`.
- Actor modules (`actor/led.py`, `actor/ky006.py`) use centralized mock classes from `utils.mocking` when `gpiozero` is not available. Mocks maintain state and log all actions.
- All mocks implement the same interface as their real hardware counterparts, making them drop-in replacements.
- For testing, use `ky001.set_mock_temperature(celsius)` to control sensor readings and validate control logic.

**Coding patterns to follow**

- Prefer centralizing hardware pins and thresholds in `config.py` rather than scattering values across modules.
- Keep `selftest()` functions simple and side-effect-limited (print + return status). This ensures the dynamic import runners can call them safely.
- Use centralized mocks from `utils.mocking` rather than inline mock implementations.
- Extract business logic into pure functions (like `determine_led_color()`) that can be tested independently.
- Use structured logging with appropriate levels (DEBUG, INFO, ERROR) and include context in error messages.
- Implement proper error handling with custom exception classes for different failure modes.
- Write logic-based tests that validate behavior, not implementation details.

**Common pitfalls**

- Do not assume presence of real hardware in CI or developer machines — rely on mock paths and classes.
- When parsing sensor output, `sensor/ky001.py` expects a `t=` prefix and performs a CRC check; avoid changing that behavior without updating callers.

**Examples**

- To change the critical temperature where the buzzer starts, edit `config.py` and modify `TEMP_CRITICAL` (e.g. `TEMP_CRITICAL = 35`).
- To add a new actor, add `actor/mydevice.py` with a `selftest()` and use the `actor/actors.py` runner to exercise it.
- To test temperature logic, use `ky001.set_mock_temperature(temp_c)` to set a specific temperature and then call `get_sensor_state()` to validate the response.
- To add a new mock hardware component, add it to `utils/mocking.py` following the pattern of existing mocks (maintain state, log actions, match real interface).

**Testing Strategy**

- Write tests that validate business logic and requirements, not implementation details.
- Use `ky001.set_mock_temperature()` to control test scenarios rather than mocking internal functions.
- Test boundary conditions (exact threshold values) and edge cases (negative temps, extreme values).
- Organize tests by behavior (e.g., `TestTemperatureThresholds`, `TestBuzzerActivation`) rather than by module.
- Ensure tests remain valid even if internal implementation changes.

See `REFACTORING.md` for detailed documentation on the architecture and testing philosophy.

If anything here is unclear or you want more examples (unit test examples, richer mock classes, or CI test matrix changes), let me know which part to expand.
