"""Actor module to control LEDs.

This module exposes a small API for working with the three LEDs used by
the project (`green`, `yellow`, `red`). On non-RPi systems the centralized
mocking infrastructure from `utils.mocking` is used; on hardware the
`gpiozero.LED` class is used.
"""
from __future__ import annotations

from time import sleep
import logging
from typing import Dict, Optional

import config
from utils.mocking import MockLED

LOG = logging.getLogger(__name__)

# Try to import real hardware, fall back to centralized mock
MOCK_MODE = False
try:
    from gpiozero import LED  # type: ignore
    LOG.debug("Using gpiozero LED hardware")
except (ImportError, RuntimeError):
    LED = MockLED  # type: ignore
    MOCK_MODE = True
    LOG.info("GPIO hardware not available - using mock LEDs")


# Initialize LED hardware objects
green_led = LED(config.LED_GREEN_PIN)
yellow_led = LED(config.LED_YELLOW_PIN)
red_led = LED(config.LED_RED_PIN)

LEDS: Dict[str, LED] = {
    "green": green_led,
    "yellow": yellow_led,
    "red": red_led,
}


def set_led(color: Optional[str]) -> None:
    """Activate the requested LED and turn off all others.

    Args:
        color: One of 'green', 'yellow', 'red' or `None` to turn all off.

    Raises:
        ValueError: If color is not recognized
    """
    # Turn off all LEDs first
    for led in LEDS.values():
        led.off()

    if color is None:
        LOG.debug("All LEDs turned off")
        return

    if color not in LEDS:
        LOG.error("Unknown LED color requested: %s", color)
        raise ValueError(f"Unknown LED color: {color}")

    LEDS[color].on()
    LOG.debug("LED set to %s", color)


def selftest() -> dict:
    """Cycle through LEDs and return a simple status dict.

    The return value is JSON-serializable to integrate with the shared
    selftest runner.
    """
    try:
        cycled = []
        for color in ["green", "yellow", "red"]:
            set_led(color)
            cycled.append(color)
            sleep(0.3)

        # Turn off all LEDs after test
        set_led(None)
        LOG.info("Selftest passed: cycled through %s", cycled)
        return {"cycled": cycled, "mode": "mock" if MOCK_MODE else "hardware"}
    except Exception as e:
        LOG.error("Selftest failed: %s", e)
        raise
