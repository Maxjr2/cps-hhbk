"""KY-001 Temperature Sensor Module.

Provides a small `read_temp()` function which returns a tuple of
(celsius, fahrenheit). On systems without a 1-Wire device the module
operates in `MOCK_MODE` and uses the centralized mocking infrastructure
from `utils.mocking`.
"""
from __future__ import annotations

import glob
import time
import logging
from typing import Tuple, Optional

import config
from utils.mocking import MockTemperatureSensor

LOG = logging.getLogger(__name__)

# SPDX-FileCopyrightText: 2019 Mikey Sklar for Adafruit Industries
# SPDX-License-Identifier: MIT

# Initialize sensor device path (with mock support)
DEVICE_FILE: Optional[str] = None
MOCK_MODE = False
_mock_sensor: Optional[MockTemperatureSensor] = None

try:
    DEVICE_FOLDER = glob.glob(
        config.TEMP_SENSOR_BASE_DIR +
        config.TEMP_SENSOR_PATTERN)[0]
    DEVICE_FILE = DEVICE_FOLDER + "/w1_slave"
    MOCK_MODE = False
    LOG.debug("Temperature sensor found at %s", DEVICE_FILE)
except (IndexError, FileNotFoundError):
    DEVICE_FILE = None
    MOCK_MODE = True
    _mock_sensor = MockTemperatureSensor(default_celsius=23.5)
    LOG.info("Temperature sensor not found - using mock mode")

# Sensor validation constants
CRC_CHECK = "YES"
TEMP_PREFIX = "t="
RETRY_DELAY = 0.2  # seconds


def read_temp_raw() -> list[str]:
    """Return raw sensor lines from the 1-Wire device or a mock payload.

    The mock payload mirrors the real device output used by the parser.
    """
    if MOCK_MODE:
        if _mock_sensor is None:
            raise RuntimeError("Mock sensor not initialized")
        return _mock_sensor.read_raw()

    if DEVICE_FILE is None:
        raise RuntimeError("Device file not available")

    try:
        with open(DEVICE_FILE, mode="r", encoding="utf-8") as sensor_file:
            lines = sensor_file.readlines()
        return lines
    except (IOError, OSError) as e:
        LOG.error("Failed to read from sensor device: %s", e)
        raise RuntimeError(f"Failed to read temperature sensor: {e}") from e


def read_temp(timeout: float = 2.0) -> Tuple[float, float]:
    """Return (celsius, fahrenheit) reading.

    If the sensor is present this function waits up to `timeout` seconds for
    a valid CRC line. On mock mode it uses the centralized mock sensor.

    Args:
        timeout: Maximum time to wait for valid CRC (seconds)

    Returns:
        Tuple of (celsius, fahrenheit)

    Raises:
        TimeoutError: If valid CRC not received within timeout
        ValueError: If temperature data parsing fails
        RuntimeError: If sensor read fails
    """
    if MOCK_MODE:
        if _mock_sensor is None:
            raise RuntimeError("Mock sensor not initialized")
        return _mock_sensor.read_temperature()

    start = time.time()
    lines = read_temp_raw()

    # Wait for valid CRC
    while not lines[0].strip().endswith(CRC_CHECK):
        if time.time() - start > timeout:
            LOG.error("Timeout waiting for valid sensor CRC")
            raise TimeoutError("Timeout waiting for valid sensor CRC")
        time.sleep(RETRY_DELAY)
        lines = read_temp_raw()

    # Parse temperature value from second line
    temp_position = lines[1].find(TEMP_PREFIX)
    if temp_position == -1:
        LOG.error("Temperature data not found in sensor output")
        raise ValueError("Temperature data not found in sensor output")

    try:
        temp_string = lines[1][temp_position + len(TEMP_PREFIX):]
        temp_celsius = float(temp_string) / 1000.0
        temp_fahrenheit = temp_celsius * 9.0 / 5.0 + 32.0
    except (ValueError, IndexError) as e:
        LOG.error("Failed to parse temperature data: %s", e)
        raise ValueError(f"Failed to parse temperature data: {e}") from e

    LOG.debug(
        "Temperature read: %.2f°C / %.2f°F",
        temp_celsius,
        temp_fahrenheit)
    return temp_celsius, temp_fahrenheit


def selftest() -> dict:
    """Run a simple read and return the observed temperature.

    Returns a JSON-serializable dict for the shared selftest runner.
    """
    try:
        temp_c, temp_f = read_temp()
        LOG.info(
            "Selftest passed: Temperature is %.2f°C / %.2f°F",
            temp_c,
            temp_f)
        return {
            "temperature_c": round(temp_c, 2),
            "temperature_f": round(temp_f, 2),
            "mode": "mock" if MOCK_MODE else "hardware"
        }
    except Exception as e:
        LOG.error("Selftest failed: %s", e)
        raise


def set_mock_temperature(celsius: float) -> None:
    """Set mock temperature for testing purposes.

    Args:
        celsius: Temperature in Celsius

    Raises:
        RuntimeError: If not in mock mode
    """
    if not MOCK_MODE or _mock_sensor is None:
        raise RuntimeError("Cannot set temperature: not in mock mode")
    _mock_sensor.set_temperature(celsius)
    LOG.debug("Mock temperature set to %.2f°C", celsius)
