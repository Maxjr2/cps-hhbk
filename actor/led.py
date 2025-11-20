"""Actor module to control LEDs.

This module exposes a small API for working with the three LEDs used by
the project (`green`, `yellow`, `red`). On non-RPi systems a lightweight
mock implementation prints state changes to stdout; on hardware the
`gpiozero.LED` class is used.
"""
from __future__ import annotations

from time import sleep
import logging
from typing import Dict, Optional

import config

LOG = logging.getLogger(__name__)

# Try to import real hardware, fall back to a local mock for portability
try:
    from gpiozero import LED  # type: ignore
except (ImportError, RuntimeError):
    class LED:  # pragma: no cover - exercised by dev machines
        def __init__(self, pin: int | None = None) -> None:
            self.pin = pin
            self.state = False

        def on(self) -> None:
            self.state = True
            LOG.info("[MOCK] LED on pin %s: ON", self.pin)

        def off(self) -> None:
            self.state = False
            LOG.info("[MOCK] LED on pin %s: OFF", self.pin)


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
    """
    # Turn off all LEDs first
    for led in LEDS.values():
        led.off()

    if color is None:
        return

    try:
        LEDS[color].on()
    except KeyError as exc:
        raise ValueError(f"Unknown LED color: {color}") from exc


def selftest() -> dict:
    """Cycle through LEDs and return a simple status dict.

    The return value is JSON-serializable to integrate with the shared
    selftest runner.
    """
    cycled = []
    for color in ["green", "yellow", "red"]:
        set_led(color)
        cycled.append(color)
        sleep(0.3)

    # Turn off all LEDs after test
    set_led(None)
    return {"cycled": cycled}
