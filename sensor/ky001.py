"""KY-001 Temperature Sensor Module."""

# SPDX-FileCopyrightText: 2019 Mikey Sklar for Adafruit Industries
# SPDX-License-Identifier: MIT

import glob
import time
import config
import os

# Initialize sensor device path (with mock support)
try:
    DEVICE_FOLDER = glob.glob(config.TEMP_SENSOR_BASE_DIR + config.TEMP_SENSOR_PATTERN)[0]
    DEVICE_FILE = DEVICE_FOLDER + '/w1_slave'
    MOCK_MODE = False
except (IndexError, FileNotFoundError):
    # No sensor found - use mock mode for testing
    DEVICE_FILE = None
    MOCK_MODE = True
    print("[MOCK] Temperature sensor not found - using simulated readings")

# Sensor validation constants
CRC_CHECK = 'YES'
TEMP_PREFIX = 't='
RETRY_DELAY = 0.2  # seconds


def read_temp_raw():
    """Reads raw temperature data from the 1-Wire sensor device."""
    if MOCK_MODE:
        # Return mock sensor data for testing
        return [
            "a1 01 4b 46 7f ff 0c 10 d8 : crc=d8 YES\n",
            "a1 01 4b 46 7f ff 0c 10 d8 t=23500\n"
        ]

    with open(DEVICE_FILE, mode='r', encoding='utf-8') as sensor_file:
        lines = sensor_file.readlines()
    return lines


def read_temp():
    """Reads and returns temperature in Celsius and Fahrenheit.

    Returns:
        tuple: (temperature_celsius, temperature_fahrenheit)
    """
    if MOCK_MODE:
        # Return mock temperature for testing (23.5°C)
        temp_celsius = 23.5
        temp_fahrenheit = temp_celsius * 9.0 / 5.0 + 32.0
        return temp_celsius, temp_fahrenheit

    # Wait for valid sensor reading (CRC check passes)
    lines = read_temp_raw()
    while not lines[0].strip().endswith(CRC_CHECK):
        time.sleep(RETRY_DELAY)
        lines = read_temp_raw()

    # Parse temperature value from second line
    temp_position = lines[1].find(TEMP_PREFIX)
    if temp_position == -1:
        raise ValueError("Temperature data not found in sensor output")

    temp_string = lines[1][temp_position + len(TEMP_PREFIX):]
    temp_celsius = float(temp_string) / 1000.0
    temp_fahrenheit = temp_celsius * 9.0 / 5.0 + 32.0

    return temp_celsius, temp_fahrenheit

def selftest():
    """Runs a self-test by reading and printing the temperature."""
    temp_c, temp_f = read_temp()
    print(f"Selftest: Temperature is {temp_c:.2f}°C / {temp_f:.2f}°F")
