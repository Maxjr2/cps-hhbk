"""KY-001 Temperature Sensor Module.

Provides a small `read_temp()` function which returns a tuple of
(celsius, fahrenheit). On systems without a 1-Wire device the module
operates in `MOCK_MODE` and returns deterministic values to make
development and tests reproducible.
"""
from __future__ import annotations

import glob
import time
import logging
from typing import Tuple

import config

LOG = logging.getLogger(__name__)

# SPDX-FileCopyrightText: 2019 Mikey Sklar for Adafruit Industries
# SPDX-License-Identifier: MIT

# Initialize sensor device path (with mock support)
try:
    DEVICE_FOLDER = glob.glob(config.TEMP_SENSOR_BASE_DIR + config.TEMP_SENSOR_PATTERN)[0]
    DEVICE_FILE = DEVICE_FOLDER + "/w1_slave"
    MOCK_MODE = False
except (IndexError, FileNotFoundError):
    DEVICE_FILE = None
    MOCK_MODE = True
    LOG.info("[MOCK] Temperature sensor not found - using simulated readings")

# Sensor validation constants
CRC_CHECK = "YES"
TEMP_PREFIX = "t="
RETRY_DELAY = 0.2  # seconds


def read_temp_raw() -> list[str]:
    """Return raw sensor lines from the 1-Wire device or a mock payload.

    The mock payload mirrors the real device output used by the parser.
    """
    if MOCK_MODE:
        return [
            "a1 01 4b 46 7f ff 0c 10 d8 : crc=d8 YES\n",
            "a1 01 4b 46 7f ff 0c 10 d8 t=23500\n",
        ]

    assert DEVICE_FILE is not None
    with open(DEVICE_FILE, mode="r", encoding="utf-8") as sensor_file:
        lines = sensor_file.readlines()
    return lines


def read_temp(timeout: float = 2.0) -> Tuple[float, float]:
    """Return (celsius, fahrenheit) reading.

    If the sensor is present this function waits up to `timeout` seconds for
    a valid CRC line. On mock mode it returns a deterministic 23.5°C value.
    """
    if MOCK_MODE:
        temp_celsius = 23.5
        temp_fahrenheit = temp_celsius * 9.0 / 5.0 + 32.0
        return temp_celsius, temp_fahrenheit

    start = time.time()
    lines = read_temp_raw()
    while not lines[0].strip().endswith(CRC_CHECK):
        if time.time() - start > timeout:
            raise TimeoutError("Timeout waiting for valid sensor CRC")
        time.sleep(RETRY_DELAY)
        lines = read_temp_raw()

    # Parse temperature value from second line
    temp_position = lines[1].find(TEMP_PREFIX)
    if temp_position == -1:
        raise ValueError("Temperature data not found in sensor output")

    temp_string = lines[1][temp_position + len(TEMP_PREFIX) :]
    temp_celsius = float(temp_string) / 1000.0
    temp_fahrenheit = temp_celsius * 9.0 / 5.0 + 32.0

    return temp_celsius, temp_fahrenheit


def selftest() -> dict:
    """Run a simple read and return the observed temperature.

    Returns a JSON-serializable dict for the shared selftest runner.
    """
    temp_c, temp_f = read_temp()
    LOG.info("Selftest: Temperature is %.2f°C / %.2f°F", temp_c, temp_f)
    return {"temperature_c": round(temp_c, 2), "temperature_f": round(temp_f, 2)}

