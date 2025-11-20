"""KY-006 Buzzer Actor Module.

Provides a small `buzz()` API and a `buzzer` instance initialized from
configuration. On non-RPi systems a mock implementation logs to the
standard logging facility instead of printing to stdout.
"""
from __future__ import annotations

from time import sleep
import logging
from typing import Literal

import config

LOG = logging.getLogger(__name__)

# Try to import real hardware, fall back to a local mock for portability
try:
    from gpiozero import PWMOutputDevice  # type: ignore
except (ImportError, RuntimeError):
    class PWMOutputDevice:  # pragma: no cover - used on dev machines
        def __init__(self, pin: int, frequency: int = 500, initial_value: float = 0.0) -> None:
            self.pin = pin
            self.frequency = frequency
            self.value = initial_value

        def __setattr__(self, name: str, val):
            object.__setattr__(self, name, val)
            if name == "value" and val > 0:
                LOG.info("[MOCK] Buzzer on pin %s: BUZZING at %sHz", self.pin, self.frequency)
            elif name == "value" and val == 0:
                LOG.info("[MOCK] Buzzer on pin %s: SILENT", self.pin)


# Initialize buzzer hardware with configured pin and frequency
buzzer = PWMOutputDevice(
    config.BUZZER_PIN,
    frequency=config.BUZZER_FREQUENCY,
    initial_value=0,
)

# Buzzer duty cycle constant
BUZZER_DUTY_CYCLE = 0.5


Action = Literal["start", "stop"]


def buzz(action: Action) -> None:
    """Controls the buzzer state.

    Args:
        action: 'start' to activate buzzer, 'stop' to deactivate
    """
    if action == "start":
        buzzer.value = BUZZER_DUTY_CYCLE
    elif action == "stop":
        buzzer.value = 0
    else:
        raise ValueError(f"Unknown action: {action}")


def selftest() -> dict:
    """Runs a self-test by activating buzzer briefly and returning a status dict."""
    buzz("start")
    sleep(0.5)
    buzz("stop")
    return {"buzzed": True}
