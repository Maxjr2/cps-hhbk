"""Logic-based tests for temperature monitoring control system.

These tests focus on business logic and behavior rather than implementation
details. They validate that the system correctly maps temperature readings
to control actions (LED colors and buzzer activation) regardless of the
underlying hardware or mocking implementation.
"""
from __future__ import annotations
from sensor import ky001
from main import (
    get_sensor_state,
    determine_led_color,
    should_activate_buzzer,
    SensorReadError,
    ActorControlError,
)
import config
import pytest

import sys
from pathlib import Path

# Ensure workspace root is on sys.path when tests run
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestTemperatureThresholds:
    """Test temperature threshold logic for LED color selection."""

    def test_cold_temperature_shows_green(self):
        """Temperature below TEMP_WARM threshold should show green LED."""
        # Test at boundary
        assert determine_led_color(config.TEMP_WARM - 0.1) == "green"
        # Test well below
        assert determine_led_color(config.TEMP_COLD) == "green"
        assert determine_led_color(20.0) == "green"

    def test_warm_temperature_shows_yellow(self):
        """Temperature between TEMP_WARM and TEMP_HOT should show yellow LED."""
        # Test at lower boundary
        assert determine_led_color(config.TEMP_WARM) == "yellow"
        # Test in middle
        assert determine_led_color(
            (config.TEMP_WARM + config.TEMP_HOT) / 2) == "yellow"
        # Test just below upper boundary
        assert determine_led_color(config.TEMP_HOT - 0.1) == "yellow"

    def test_hot_temperature_shows_red(self):
        """Temperature at or above TEMP_HOT should show red LED."""
        # Test at boundary
        assert determine_led_color(config.TEMP_HOT) == "red"
        # Test above boundary
        assert determine_led_color(config.TEMP_HOT + 5) == "red"
        # Test at critical
        assert determine_led_color(config.TEMP_CRITICAL) == "red"


class TestBuzzerActivation:
    """Test buzzer activation logic based on critical temperature."""

    def test_buzzer_off_below_critical(self):
        """Buzzer should be off when temperature is below critical threshold."""
        assert should_activate_buzzer(config.TEMP_CRITICAL - 0.1) is False
        assert should_activate_buzzer(config.TEMP_HOT) is False
        assert should_activate_buzzer(config.TEMP_WARM) is False
        assert should_activate_buzzer(20.0) is False

    def test_buzzer_on_at_critical(self):
        """Buzzer should activate exactly at critical threshold."""
        assert should_activate_buzzer(config.TEMP_CRITICAL) is True

    def test_buzzer_on_above_critical(self):
        """Buzzer should remain on when temperature exceeds critical threshold."""
        assert should_activate_buzzer(config.TEMP_CRITICAL + 1) is True
        assert should_activate_buzzer(config.TEMP_CRITICAL + 10) is True
        assert should_activate_buzzer(50.0) is True


class TestSensorStateIntegration:
    """Integration tests for complete sensor state logic."""

    def test_cold_state_configuration(self):
        """Cold temperature should result in green LED and no buzzer."""
        # Set mock temperature to cold value
        ky001.set_mock_temperature(20.0)

        state = get_sensor_state()

        assert state["temperature_c"] == 20.0
        assert state["led"] == "green"
        assert state["buzzer_on"] is False
        assert "error" not in state

    def test_warm_state_configuration(self):
        """Warm temperature should result in yellow LED and no buzzer."""
        # Set mock temperature to warm value
        test_temp = (config.TEMP_WARM + config.TEMP_HOT) / 2
        ky001.set_mock_temperature(test_temp)

        state = get_sensor_state()

        assert state["temperature_c"] == test_temp
        assert state["led"] == "yellow"
        assert state["buzzer_on"] is False
        assert "error" not in state

    def test_hot_state_configuration(self):
        """Hot temperature should result in red LED and no buzzer."""
        # Set mock temperature to hot but not critical
        test_temp = config.TEMP_HOT + 1
        ky001.set_mock_temperature(test_temp)

        state = get_sensor_state()

        assert state["temperature_c"] == test_temp
        assert state["led"] == "red"
        assert state["buzzer_on"] is False
        assert "error" not in state

    def test_critical_state_configuration(self):
        """Critical temperature should result in red LED and active buzzer."""
        # Set mock temperature to critical
        ky001.set_mock_temperature(config.TEMP_CRITICAL)

        state = get_sensor_state()

        assert state["temperature_c"] == config.TEMP_CRITICAL
        assert state["led"] == "red"
        assert state["buzzer_on"] is True
        assert "error" not in state

    def test_fahrenheit_conversion(self):
        """Verify Fahrenheit conversion is accurate."""
        test_temp = 25.0
        ky001.set_mock_temperature(test_temp)

        state = get_sensor_state()

        expected_f = test_temp * 9.0 / 5.0 + 32.0
        assert abs(state["temperature_f"] - expected_f) < 0.01


class TestThresholdBoundaries:
    """Test behavior at exact threshold boundaries."""

    def test_temp_warm_boundary(self):
        """Test exact TEMP_WARM boundary behavior."""
        # Just below - should be green
        ky001.set_mock_temperature(config.TEMP_WARM - 0.01)
        state = get_sensor_state()
        assert state["led"] == "green"

        # At boundary - should be yellow
        ky001.set_mock_temperature(config.TEMP_WARM)
        state = get_sensor_state()
        assert state["led"] == "yellow"

    def test_temp_hot_boundary(self):
        """Test exact TEMP_HOT boundary behavior."""
        # Just below - should be yellow
        ky001.set_mock_temperature(config.TEMP_HOT - 0.01)
        state = get_sensor_state()
        assert state["led"] == "yellow"

        # At boundary - should be red
        ky001.set_mock_temperature(config.TEMP_HOT)
        state = get_sensor_state()
        assert state["led"] == "red"

    def test_temp_critical_boundary(self):
        """Test exact TEMP_CRITICAL boundary behavior."""
        # Just below - buzzer off
        ky001.set_mock_temperature(config.TEMP_CRITICAL - 0.01)
        state = get_sensor_state()
        assert state["buzzer_on"] is False

        # At boundary - buzzer on
        ky001.set_mock_temperature(config.TEMP_CRITICAL)
        state = get_sensor_state()
        assert state["buzzer_on"] is True


class TestTemperatureRangeScenarios:
    """Test various temperature scenarios across the full range."""

    @pytest.mark.parametrize("temp,expected_led,expected_buzzer", [
        (15.0, "green", False),
        (21.0, "green", False),
        (25.99, "green", False),
        (26.0, "yellow", False),
        (28.0, "yellow", False),
        (30.99, "yellow", False),
        (31.0, "red", False),
        (33.0, "red", False),
        (34.99, "red", False),
        (35.0, "red", True),
        (40.0, "red", True),
        (50.0, "red", True),
    ])
    def test_temperature_scenarios(self, temp, expected_led, expected_buzzer):
        """Test various temperature scenarios."""
        ky001.set_mock_temperature(temp)
        state = get_sensor_state()

        assert state["temperature_c"] == temp
        assert state["led"] == expected_led, \
            f"At {temp}°C, expected LED {expected_led} but got {state['led']}"
        assert state["buzzer_on"] == expected_buzzer, \
            f"At {temp}°C, expected buzzer={expected_buzzer} but got {state['buzzer_on']}"


class TestErrorConditions:
    """Test error handling and edge cases."""

    def test_sensor_returns_consistent_structure(self):
        """Verify sensor state always returns expected keys."""
        ky001.set_mock_temperature(25.0)
        state = get_sensor_state()

        required_keys = ["temperature_c", "temperature_f", "led", "buzzer_on"]
        for key in required_keys:
            assert key in state, f"Missing required key: {key}"

    def test_negative_temperature(self):
        """System should handle negative temperatures correctly."""
        ky001.set_mock_temperature(-5.0)
        state = get_sensor_state()

        assert state["temperature_c"] == -5.0
        assert state["led"] == "green"
        assert state["buzzer_on"] is False

    def test_extreme_high_temperature(self):
        """System should handle extremely high temperatures."""
        ky001.set_mock_temperature(100.0)
        state = get_sensor_state()

        assert state["temperature_c"] == 100.0
        assert state["led"] == "red"
        assert state["buzzer_on"] is True
