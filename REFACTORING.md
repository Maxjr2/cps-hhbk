# Refactoring Documentation

## Overview

This document describes the refactoring performed to improve the codebase's architecture, testing strategy, and error handling.

## Changes Summary

### 1. Centralized Mocking Infrastructure

**File:** `utils/mocking.py`

**Motivation:** Previously, mock implementations for hardware components (LEDs, buzzers, sensors) were scattered across individual modules with inline class definitions. This made the code harder to maintain and test.

**Solution:** Created a centralized mocking module that provides:
- `MockLED` - Simulates GPIO LED behavior with state tracking
- `MockPWMOutputDevice` - Simulates PWM buzzer control
- `MockTemperatureSensor` - Simulates temperature sensor with configurable readings
- Hardware detection utilities to determine what's available

**Benefits:**
- Single source of truth for mock implementations
- Easier to test and maintain
- Consistent behavior across all mock objects
- Better separation of concerns

### 2. Improved Logging and Error Handling

**Affected Files:** `main.py`, `sensor/ky001.py`, `actor/led.py`, `actor/ky006.py`

**Changes Made:**

#### Custom Exception Classes
```python
class TemperatureMonitorError(Exception):
    """Base exception for temperature monitoring errors."""

class SensorReadError(TemperatureMonitorError):
    """Exception raised when sensor reading fails."""

class ActorControlError(TemperatureMonitorError):
    """Exception raised when actor control fails."""
```

#### Structured Logging
- **DEBUG**: Low-level operational details (sensor reads, mock initializations)
- **INFO**: Important state changes and successful operations
- **ERROR**: Failures with full exception context (`exc_info=True`)

#### Error Recovery
- Graceful degradation: If LED control fails, buzzer control is still attempted
- Comprehensive error messages that include context
- Proper exception chaining with `from` keyword

### 3. Logic Extraction in Main Module

**File:** `main.py`

**Extracted Functions:**
```python
def determine_led_color(temperature_c: float) -> str:
    """Pure function that maps temperature to LED color."""
    
def should_activate_buzzer(temperature_c: float) -> bool:
    """Pure function that determines buzzer activation."""
```

**Benefits:**
- Business logic separated from I/O operations
- Functions are easily testable in isolation
- Clear, single-responsibility functions
- Makes the code easier to understand and modify

### 4. Comprehensive Logic-Based Testing

**File:** `tests/test_logic.py`

**Philosophy:** Tests should validate business logic and behavior, not implementation details. This ensures tests remain valid even when the underlying implementation changes.

**Test Coverage:**

#### Temperature Threshold Tests
- Validates LED color selection at various temperature ranges
- Tests exact boundary conditions
- Ensures consistent behavior across the full temperature spectrum

#### Buzzer Activation Tests
- Verifies buzzer activates at critical temperature
- Tests all temperature ranges for correct buzzer state

#### Integration Tests
- Full end-to-end scenarios from temperature reading to control actions
- Tests all temperature zones (cold, warm, hot, critical)
- Validates complete system state

#### Edge Case Tests
- Negative temperatures
- Extreme high temperatures
- Exact threshold boundaries
- Parametrized testing for comprehensive coverage

**Test Statistics:**
- 29 new logic-based tests
- 100% pass rate
- Covers all business logic paths

### 5. Sensor and Actor Module Updates

**Sensor Changes (`sensor/ky001.py`):**
- Uses centralized `MockTemperatureSensor`
- Added `set_mock_temperature()` for testing
- Improved error messages and logging
- Better exception handling for file I/O errors

**Actor Changes (`actor/led.py`, `actor/ky006.py`):**
- Use centralized mock classes
- Added validation and better error messages
- Enhanced logging at appropriate levels
- Self-tests now report mode (mock/hardware)

## Testing Strategy

### Old Approach
- Tests focused on implementation (checking mock behavior)
- Tightly coupled to how mocks were implemented
- Tests would break if mock implementation changed

### New Approach
- Tests focus on business logic and requirements
- Uses the mock's `set_temperature()` API to control scenarios
- Tests validate outputs based on inputs, not how they're produced
- Implementation can change without breaking tests

### Example Test
```python
def test_critical_state_configuration(self):
    """Critical temperature should result in red LED and active buzzer."""
    ky001.set_mock_temperature(config.TEMP_CRITICAL)
    
    state = get_sensor_state()
    
    assert state["temperature_c"] == config.TEMP_CRITICAL
    assert state["led"] == "red"
    assert state["buzzer_on"] is True
```

This test:
- Sets up a specific scenario (critical temperature)
- Validates the expected behavior (red LED + buzzer)
- Doesn't care about how the temperature is read or mocked
- Will remain valid even if we change the sensor implementation

## Running Tests

```bash
# Run all tests
pytest -v

# Run only logic tests
pytest tests/test_logic.py -v

# Run tests with coverage
pytest --cov=. --cov-report=html
```

## Running Selftests

```bash
# Test all actors
python -m actor.actors

# Test all sensors
python -m sensor.sensors

# Run main selftest
python -c "from main import run_selftests; run_selftests()"
```

## Future Improvements

1. **Add more integration tests** for hardware failure scenarios
2. **Performance tests** to ensure response times are acceptable
3. **Configuration validation** to catch invalid threshold values at startup
4. **Logging configuration** to support different log levels in production vs development
5. **Mock recording/playback** for capturing real hardware behavior and replaying it in tests

## Migration Guide

If you're updating existing code that used the old inline mocks:

### Before
```python
try:
    from gpiozero import LED
except ImportError:
    class LED:  # inline mock
        ...
```

### After
```python
from utils.mocking import MockLED

try:
    from gpiozero import LED
except ImportError:
    LED = MockLED  # use centralized mock
```

### Testing Before
```python
def test_led():
    # Tests checked mock implementation details
    actor_led.set_led("green")
    assert actor_led.LEDS["green"].state is True
```

### Testing After
```python
def test_led_logic():
    # Tests validate business logic
    ky001.set_mock_temperature(20.0)  # cold
    state = get_sensor_state()
    assert state["led"] == "green"  # don't care how, just that it's green
```

## Benefits Summary

1. **Better Separation of Concerns**: Mocking, business logic, and I/O are clearly separated
2. **Easier Testing**: Business logic can be tested in isolation without hardware
3. **More Maintainable**: Changes to implementation don't break tests
4. **Better Error Handling**: Structured exceptions and comprehensive logging
5. **Clearer Code**: Pure functions make logic easier to understand and reason about
6. **More Robust**: Tests cover edge cases and boundary conditions thoroughly
