"""Hardware configuration for all sensors and actors.

Centralized GPIO pin assignments, sensor device discovery patterns and
temperature threshold constants. Keep names in ALL_CAPS to make it clear
these are configuration values.
"""
from __future__ import annotations

from typing import Final

# Actor (Output) Pins
LED_GREEN_PIN: Final[int] = 17
LED_YELLOW_PIN: Final[int] = 27
LED_RED_PIN: Final[int] = 22
BUZZER_PIN: Final[int] = 24
BUZZER_FREQUENCY: Final[int] = 500  # Hz

# Sensor (Input) Paths
TEMP_SENSOR_BASE_DIR: Final[str] = "/sys/bus/w1/devices/"
TEMP_SENSOR_PATTERN: Final[str] = "28*"

# Temperature Thresholds (Celsius)
TEMP_COLD: Final[float] = 21.0
TEMP_WARM: Final[float] = 26.0
TEMP_HOT: Final[float] = 31.0
TEMP_CRITICAL: Final[float] = 35.0
