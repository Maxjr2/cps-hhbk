"""Hardware configuration for all sensors and actors.

This file contains all GPIO pin assignments in one place for easy maintenance.
Modify these values to match your hardware setup.
"""

# Actor (Output) Pins
LED_GREEN_PIN = 17
LED_YELLOW_PIN = 27
LED_RED_PIN = 22
BUZZER_PIN = 24
BUZZER_FREQUENCY = 500  # Hz

# Sensor (Input) Paths
TEMP_SENSOR_BASE_DIR = '/sys/bus/w1/devices/'
TEMP_SENSOR_PATTERN = '28*'

# Temperature Thresholds (Celsius)
TEMP_COLD = 21
TEMP_WARM = 26
TEMP_HOT = 31
TEMP_CRITICAL = 35
