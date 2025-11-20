"""Main application for temperature monitoring and control.

The public API is intentionally small: `get_sensor_state()` performs a
single read and applies actor controls; it returns a small dict describing
the observed state. Side effects (LED/buzzer) are performed but callers
can examine the returned dict for programmatic checks.
"""
from __future__ import annotations

from typing import Dict, Any, Optional
import logging

from sensor import ky001
from actor import led as actor_led
from actor import ky006 as actor_buzzer
import config

LOG = logging.getLogger(__name__)


class TemperatureMonitorError(Exception):
    """Base exception for temperature monitoring errors."""
    pass


class SensorReadError(TemperatureMonitorError):
    """Exception raised when sensor reading fails."""
    pass


class ActorControlError(TemperatureMonitorError):
    """Exception raised when actor control fails."""
    pass


def determine_led_color(temperature_c: float) -> str:
    """Determine LED color based on temperature thresholds.

    Args:
        temperature_c: Temperature in Celsius

    Returns:
        LED color: 'green', 'yellow', or 'red'
    """
    if temperature_c < config.TEMP_WARM:
        return "green"
    elif temperature_c < config.TEMP_HOT:
        return "yellow"
    else:
        return "red"


def should_activate_buzzer(temperature_c: float) -> bool:
    """Determine if buzzer should be activated based on temperature.

    Args:
        temperature_c: Temperature in Celsius

    Returns:
        True if temperature is at or above critical threshold
    """
    return temperature_c >= config.TEMP_CRITICAL


def get_sensor_state() -> Dict[str, Any]:
    """Read temperature and control LED + buzzer.

    Returns a dict with keys: `temperature_c`, `temperature_f`, `led`,
    `buzzer_on`, and `error` (if any error occurred).

    Raises:
        SensorReadError: If temperature sensor reading fails
        ActorControlError: If LED or buzzer control fails
    """
    error: Optional[str] = None

    try:
        temp_c, temp_f = ky001.read_temp()
        LOG.debug("Temperature read: %.2f°C / %.2f°F", temp_c, temp_f)
    except Exception as e:
        LOG.error("Failed to read temperature sensor: %s", e, exc_info=True)
        raise SensorReadError(f"Failed to read temperature: {e}") from e

    # Determine control actions based on temperature
    try:
        color = determine_led_color(temp_c)
        buzzer_on = should_activate_buzzer(temp_c)

        LOG.debug(
            "Control decision: temp=%.2f°C -> LED=%s, buzzer=%s",
            temp_c, color, buzzer_on
        )
    except Exception as e:
        LOG.error("Failed to determine control actions: %s", e, exc_info=True)
        raise ActorControlError(
            f"Failed to determine control actions: {e}") from e

    # Apply LED control
    try:
        actor_led.set_led(color)
    except Exception as e:
        LOG.error("Failed to control LED: %s", e, exc_info=True)
        error = f"LED control failed: {e}"
        # Don't raise - continue to try buzzer

    # Apply buzzer control
    try:
        actor_buzzer.buzz("start" if buzzer_on else "stop")
    except Exception as e:
        LOG.error("Failed to control buzzer: %s", e, exc_info=True)
        if error:
            error += f"; Buzzer control failed: {e}"
        else:
            error = f"Buzzer control failed: {e}"

    LOG.info(
        "Sensor state: %.2f°C -> LED=%s, buzzer=%s%s",
        temp_c, color, buzzer_on, f" (errors: {error})" if error else ""
    )

    result = {
        "temperature_c": temp_c,
        "temperature_f": temp_f,
        "led": color,
        "buzzer_on": buzzer_on,
    }

    if error:
        result["error"] = error
        raise ActorControlError(error)

    return result


def run_selftests() -> None:
    """Run selftests for actors and sensors.

    This is a convenience wrapper that calls the module-level `selftest()`
    functions. Each selftest is expected to be side-effect limited and may
    return a small value; here we only invoke them for their console
    output.

    Raises:
        Exception: If any selftest fails
    """
    LOG.info("Running component selftests...")

    try:
        LOG.info("Testing LED actor...")
        actor_led.selftest()
    except Exception as e:
        LOG.error("LED selftest failed: %s", e, exc_info=True)
        raise

    try:
        LOG.info("Testing buzzer actor...")
        actor_buzzer.selftest()
    except Exception as e:
        LOG.error("Buzzer selftest failed: %s", e, exc_info=True)
        raise

    try:
        LOG.info("Testing temperature sensor...")
        ky001.selftest()
    except Exception as e:
        LOG.error("Temperature sensor selftest failed: %s", e, exc_info=True)
        raise

    LOG.info("All selftests completed successfully")
