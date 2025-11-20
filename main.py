"""Main application for temperature monitoring and control.

The public API is intentionally small: `get_sensor_state()` performs a
single read and applies actor controls; it returns a small dict describing
the observed state. Side effects (LED/buzzer) are performed but callers
can examine the returned dict for programmatic checks.
"""
from __future__ import annotations

from typing import Dict, Any
import logging

from sensor import ky001
from actor import led as actor_led
from actor import ky006 as actor_buzzer
import config

LOG = logging.getLogger(__name__)


def get_sensor_state() -> Dict[str, Any]:
    """Read temperature and control LED + buzzer.

    Returns a dict with keys: `temperature_c`, `temperature_f`, `led`,
    `buzzer_on`.
    """
    temp_c, temp_f = ky001.read_temp()

    # Decide LED color
    if temp_c < config.TEMP_WARM:
        color = "green"
    elif temp_c < config.TEMP_HOT:
        color = "yellow"
    else:
        color = "red"

    actor_led.set_led(color)

    buzzer_on = temp_c >= config.TEMP_CRITICAL
    actor_buzzer.buzz("start" if buzzer_on else "stop")

    LOG.info("Sensor read: %.2f°C -> LED=%s buzzer=%s", temp_c, color, buzzer_on)

    return {
        "temperature_c": temp_c,
        "temperature_f": temp_f,
        "led": color,
        "buzzer_on": buzzer_on,
    }


def run_selftests() -> None:
    """Run selftests for actors and sensors.

    This is a convenience wrapper that calls the module-level `selftest()`
    functions. Each selftest is expected to be side-effect limited and may
    return a small value; here we only invoke them for their console
    output.
    """
    actor_led.selftest()
    actor_buzzer.selftest()
    ky001.selftest()

