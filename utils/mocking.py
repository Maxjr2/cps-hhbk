"""Centralized hardware mocking infrastructure.

This module provides mock implementations for hardware components (LEDs, PWM
devices, sensors) that would normally require Raspberry Pi GPIO access. These
mocks enable development and testing on systems without hardware.

The mocks are designed to be behavioral - they maintain state and log actions
in a way that allows testing the control logic without needing physical hardware.
"""
from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any

LOG = logging.getLogger(__name__)


class MockLED:
    """Mock implementation of gpiozero.LED.

    Maintains LED state and logs transitions for testing and development.
    """

    def __init__(self, pin: Optional[int] = None) -> None:
        """Initialize mock LED.

        Args:
            pin: GPIO pin number (stored for logging purposes)
        """
        self.pin = pin
        self.state = False
        LOG.debug("MockLED initialized on pin %s", self.pin)

    def on(self) -> None:
        """Turn LED on and log the action."""
        self.state = True
        LOG.info("[MOCK] LED on pin %s: ON", self.pin)

    def off(self) -> None:
        """Turn LED off and log the action."""
        self.state = False
        LOG.info("[MOCK] LED on pin %s: OFF", self.pin)


class MockPWMOutputDevice:
    """Mock implementation of gpiozero.PWMOutputDevice for buzzers.

    Simulates PWM control with duty cycle management and logging.
    """

    def __init__(
        self,
        pin: int,
        frequency: int = 500,
        initial_value: float = 0.0
    ) -> None:
        """Initialize mock PWM device.

        Args:
            pin: GPIO pin number
            frequency: PWM frequency in Hz
            initial_value: Initial duty cycle (0.0 to 1.0)
        """
        self.pin = pin
        self.frequency = frequency
        self._value = initial_value
        LOG.debug(
            "MockPWMOutputDevice initialized on pin %s at %sHz",
            self.pin,
            self.frequency
        )

    @property
    def value(self) -> float:
        """Get current PWM duty cycle."""
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        """Set PWM duty cycle and log state changes.

        Args:
            val: Duty cycle value (0.0 to 1.0)
        """
        self._value = val
        if val > 0:
            LOG.info(
                "[MOCK] Buzzer on pin %s: BUZZING at %sHz (duty=%.2f)",
                self.pin,
                self.frequency,
                val
            )
        else:
            LOG.info("[MOCK] Buzzer on pin %s: SILENT", self.pin)


class MockTemperatureSensor:
    """Mock temperature sensor for testing and development.

    Provides configurable temperature readings that can be controlled
    programmatically for testing different scenarios.
    """

    def __init__(self, default_celsius: float = 23.5) -> None:
        """Initialize mock sensor.

        Args:
            default_celsius: Default temperature reading in Celsius
        """
        self._temperature_c = default_celsius
        LOG.debug(
            "MockTemperatureSensor initialized at %.2f°C",
            default_celsius)

    def set_temperature(self, celsius: float) -> None:
        """Set the temperature for testing purposes.

        Args:
            celsius: Temperature in Celsius
        """
        self._temperature_c = celsius
        LOG.debug("MockTemperatureSensor temperature set to %.2f°C", celsius)

    def read_raw(self) -> List[str]:
        """Return mock raw sensor data in 1-Wire format.

        Returns:
            List of strings mimicking real sensor output
        """
        # Convert temperature to the integer format used by real sensor
        temp_int = int(self._temperature_c * 1000)
        return [
            "a1 01 4b 46 7f ff 0c 10 d8 : crc=d8 YES\n",
            f"a1 01 4b 46 7f ff 0c 10 d8 t={temp_int}\n",
        ]

    def read_temperature(self) -> tuple[float, float]:
        """Read temperature in both Celsius and Fahrenheit.

        Returns:
            Tuple of (celsius, fahrenheit)
        """
        celsius = self._temperature_c
        fahrenheit = celsius * 9.0 / 5.0 + 32.0
        LOG.debug(
            "MockTemperatureSensor read: %.2f°C / %.2f°F",
            celsius,
            fahrenheit
        )
        return celsius, fahrenheit


# Hardware detection helper
def is_hardware_available() -> Dict[str, bool]:
    """Check which hardware modules are available.

    Returns:
        Dictionary mapping hardware type to availability status
    """
    availability = {
        "gpiozero": False,
        "w1_sensor": False,
    }

    # Check for gpiozero
    try:
        import gpiozero  # type: ignore # noqa: F401
        availability["gpiozero"] = True
    except (ImportError, RuntimeError):
        pass

    # Check for 1-Wire sensor
    import glob
    import config
    try:
        devices = glob.glob(
            config.TEMP_SENSOR_BASE_DIR + config.TEMP_SENSOR_PATTERN
        )
        availability["w1_sensor"] = len(devices) > 0
    except (FileNotFoundError, PermissionError):
        pass

    return availability


def get_hardware_status() -> Dict[str, Any]:
    """Get detailed hardware availability status.

    Returns:
        Dictionary with hardware availability and mock mode indicators
    """
    availability = is_hardware_available()
    return {
        "hardware_available": availability,
        "mock_mode": {
            "gpio": not availability["gpiozero"],
            "temperature_sensor": not availability["w1_sensor"],
        },
        "ready": True,
    }
