"""KY-006 Buzzer Actor Module.

Provides a small `buzz()` API and a `buzzer` instance initialized from
configuration. On non-RPi systems the centralized mocking infrastructure
from `utils.mocking` is used instead of gpiozero.
"""
from __future__ import annotations

from time import sleep
import logging
from typing import Literal

import config
from utils.mocking import MockPWMOutputDevice

LOG = logging.getLogger(__name__)

# Try to import real hardware, fall back to centralized mock
MOCK_MODE = False
try:
    from gpiozero import PWMOutputDevice  # type: ignore
    LOG.debug("Using gpiozero PWM hardware")
except (ImportError, RuntimeError):
    PWMOutputDevice = MockPWMOutputDevice  # type: ignore
    MOCK_MODE = True
    LOG.info("GPIO hardware not available - using mock PWM device")


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

    Raises:
        ValueError: If action is not 'start' or 'stop'
    """
    if action == "start":
        buzzer.value = BUZZER_DUTY_CYCLE
        LOG.debug("Buzzer started")
    elif action == "stop":
        buzzer.value = 0
        LOG.debug("Buzzer stopped")
    else:
        LOG.error("Unknown buzzer action: %s", action)
        raise ValueError(f"Unknown action: {action}")


def selftest() -> dict:
    """Runs a self-test by activating buzzer briefly and returning a status dict."""
    try:
        buzz("start")
        sleep(0.5)
        buzz("stop")
        LOG.info("Selftest passed: buzzer activated successfully")
        return {"buzzed": True, "mode": "mock" if MOCK_MODE else "hardware"}
    except Exception as e:
        LOG.error("Selftest failed: %s", e)
        raise
