"""Basic tests covering sensor and actor mocks."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure workspace root is on sys.path when tests run
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from actor import led as actor_led
from actor import ky006 as actor_buzzer
from sensor import ky001


def test_sensor_mock_read_temp():
    c, f = ky001.read_temp()
    # In mock mode the sensor returns 23.5°C -> 74.3°F
    assert isinstance(c, float)
    assert abs(c - 23.5) < 0.001
    assert abs(f - (c * 9.0 / 5.0 + 32.0)) < 0.001

def test_actor_led_and_buzzer():
    # cycle LEDs
    actor_led.set_led("green")
    assert actor_led.LEDS["green"].state is True
    actor_led.set_led(None)
    assert all(not led.state for led in actor_led.LEDS.values())

    # buzzer off then on
    actor_buzzer.buzz("stop")
    assert getattr(actor_buzzer.buzzer, "value") == 0
    actor_buzzer.buzz("start")
    assert getattr(actor_buzzer.buzzer, "value") == actor_buzzer.BUZZER_DUTY_CYCLE
