# Actors API Reference

Complete API documentation for all actor modules in the CPS HHBK system.

## Module: `actors.led`

LED controller module for visual temperature indication using RGB LEDs.

**Module Path:** `actors/led.py`

**Import:**
```python
import actors.led
from actors import led
```

### Dependencies

```python
from time import sleep
from gpiozero import LED
```

**Required Libraries:**
- `gpiozero`: GPIO interface library ([documentation](https://gpiozero.readthedocs.io/))

**Installation:**
```bash
pip install gpiozero
```

---

### Module-Level Objects

#### `green`

Green LED object for cool temperature indication.

**Type:** `gpiozero.LED`

**Declaration:**
```python
green = LED()
```

!!! danger "Missing Pin Configuration"
    The current code creates LED object without pin number. Must be updated:
    ```python
    green = LED(17)  # GPIO 17
    ```

**Usage:**
```python
actors.led.green.on()   # Turn on
actors.led.green.off()  # Turn off
actors.led.green.toggle()  # Switch state
```

**Properties:**
```python
actors.led.green.is_lit  # bool: True if LED is on
actors.led.green.pin     # Pin: GPIO pin object
actors.led.green.value   # int: 0 (off) or 1 (on)
```

---

#### `yellow`

Yellow LED object for warm temperature indication.

**Type:** `gpiozero.LED`

**Declaration:**
```python
yellow = LED()
```

!!! danger "Missing Pin Configuration"
    Must be updated with GPIO pin number:
    ```python
    yellow = LED(27)  # GPIO 27
    ```

**Usage:**
```python
actors.led.yellow.on()
actors.led.yellow.off()
```

---

#### `red`

Red LED object for hot temperature indication.

**Type:** `gpiozero.LED`

**Declaration:**
```python
red = LED()
```

!!! danger "Missing Pin Configuration"
    Must be updated with GPIO pin number:
    ```python
    red = LED(22)  # GPIO 22
    ```

**Usage:**
```python
actors.led.red.on()
actors.led.red.off()
```

---

### Functions

#### `set_led(color)`

Set LED to specified color, turning off all others.

**Signature:**
```python
def set_led(color: str) -> None
```

**Parameters:**

| Parameter | Type | Description | Valid Values |
|-----------|------|-------------|--------------|
| `color` | `str` | LED color to activate | `"green"`, `"yellow"`, `"red"`, `None` |

**Returns:**
- `None`

**Behavior:**

1. **Reset Phase**: All LEDs turned off
   ```python
   green.off()
   yellow.off()
   red.off()
   ```

2. **Activation Phase**: Selected LED turned on
   ```python
   if color == "green":
       green.on()
   elif color == "yellow":
       yellow.on()
   elif color == "red":
       red.on()
   ```

3. **Invalid Input**: All LEDs remain off

**State Transition Table:**

| Input Color | Green LED | Yellow LED | Red LED |
|-------------|-----------|------------|---------|
| `"green"` | ON | OFF | OFF |
| `"yellow"` | OFF | ON | OFF |
| `"red"` | OFF | OFF | ON |
| `None` | OFF | OFF | OFF |
| Other | OFF | OFF | OFF |

**Examples:**

```python
import actors.led

# Turn on green LED (cool)
actors.led.set_led("green")

# Turn on yellow LED (warm)
actors.led.set_led("yellow")

# Turn on red LED (hot)
actors.led.set_led("red")

# Turn off all LEDs
actors.led.set_led(None)
actors.led.set_led("invalid")  # Also turns all off
```

**Implementation:**
```python
def set_led(color):
    """Sets the LED color based on the input string."""
    green.off()
    yellow.off()
    red.off()
    if color == "green":
        green.on()
    elif color == "yellow":
        yellow.on()
    elif color == "red":
        red.on()
```

**Raises:**
- No exceptions raised
- Invalid colors silently ignored (all LEDs off)

**Side Effects:**
- Modifies GPIO pin states
- Changes LED hardware state
- All LEDs reset before activation

**Performance:**
- Execution time: < 1ms
- GPIO switching: < 100μs per operation

---

#### `selftest()`

Run LED self-test sequence to verify hardware functionality.

**Signature:**
```python
def selftest() -> None
```

**Parameters:**
- None

**Returns:**
- `None`

**Behavior:**

Cycles through all LED colors with 1-second delays:

1. **Green LED**: ON for 1 second
2. **Yellow LED**: ON for 1 second
3. **Red LED**: ON for 1 second
4. **All OFF**: Final state

**Total Duration:** 3 seconds

**Sequence Diagram:**

```
Timeline:  0s    1s    2s    3s
           |     |     |     |
Green:    ████
Yellow:         ████
Red:                  ████
```

**Example:**
```python
import actors.led

# Run hardware test
print("Testing LEDs...")
actors.led.selftest()
print("Test complete")
```

**Implementation:**
```python
def selftest():
    """Runs a self-test by cycling through the LED colors."""
    set_led("green")
    sleep(1)
    set_led("yellow")
    sleep(1)
    set_led("red")
    sleep(1)
    set_led(None)
```

**Use Cases:**

1. **Initial Setup**: Verify wiring during installation
2. **Debugging**: Check LED functionality
3. **Startup Routine**: Visual confirmation system is ready
4. **Maintenance**: Periodic hardware verification

**Expected Output:**
- Visual: All three LEDs should light in sequence
- Duration: Exactly 3 seconds
- Final state: All LEDs off

**Troubleshooting:**

| Observation | Possible Cause | Solution |
|-------------|----------------|----------|
| No LEDs light | No power or wrong pins | Check wiring, update pin numbers |
| Only some LEDs work | Faulty LED or connection | Check specific LED and wiring |
| LEDs very dim | Wrong resistor value | Use 220Ω resistors |
| Wrong LED lights | Pin mismatch | Verify GPIO numbers match wiring |

---

### Usage Patterns

#### Pattern 1: Direct Control

```python
import actors.led

# Explicit LED control
actors.led.set_led("green")
time.sleep(2)
actors.led.set_led("yellow")
time.sleep(2)
actors.led.set_led("red")
time.sleep(2)
actors.led.set_led(None)
```

#### Pattern 2: State-Based Control

```python
import actors.led

def indicate_status(status):
    """Map status to LED color"""
    status_map = {
        'cool': 'green',
        'warm': 'yellow',
        'hot': 'red',
        'off': None
    }
    actors.led.set_led(status_map.get(status, None))

indicate_status('cool')
```

#### Pattern 3: Temperature-Driven

```python
import actors.led
import sensors.ky001

def update_led_from_temp():
    """Update LED based on current temperature"""
    temp_c = sensors.ky001.read_temp()[0]

    if temp_c < 21:
        actors.led.set_led("green")
    elif temp_c < 26:
        actors.led.set_led("yellow")
    else:
        actors.led.set_led("red")
```

#### Pattern 4: Blinking/Flashing

```python
import actors.led
import time

def blink_led(color, times=3, interval=0.5):
    """Blink specified LED"""
    for _ in range(times):
        actors.led.set_led(color)
        time.sleep(interval)
        actors.led.set_led(None)
        time.sleep(interval)

# Flash red as warning
blink_led("red", times=5, interval=0.3)
```

#### Pattern 5: Cleanup Handler

```python
import actors.led
import atexit

def cleanup_leds():
    """Turn off all LEDs on exit"""
    actors.led.set_led(None)

# Register cleanup
atexit.register(cleanup_leds)

# Or use try-finally
try:
    # Main program
    actors.led.set_led("green")
    # ...
finally:
    actors.led.set_led(None)
```

---

### Direct GPIO Access

For advanced use, access GPIO directly:

#### Low-Level Control

```python
import actors.led

# Direct LED object manipulation
actors.led.green.on()
actors.led.green.off()
actors.led.green.toggle()

# Check state
if actors.led.green.is_lit:
    print("Green LED is on")

# PWM control (if using PWMLED)
# actors.led.green.value = 0.5  # 50% brightness
```

#### Multiple LEDs Simultaneously

```python
# Turn on multiple LEDs (override standard behavior)
actors.led.green.on()
actors.led.yellow.on()
# Both green and yellow now on
```

---

### gpiozero LED Methods

The `LED` objects support all gpiozero LED methods:

#### Basic Methods

```python
led.on()           # Turn on
led.off()          # Turn off
led.toggle()       # Switch state
led.blink(on_time=1, off_time=1)  # Blink pattern
```

#### Properties

```python
led.is_lit         # bool: LED state
led.pin            # Pin: GPIO pin object
led.value          # float: 0 (off) or 1 (on)
```

#### Events

```python
# Callback when LED turns on
led.when_activated = lambda: print("LED on")

# Callback when LED turns off
led.when_deactivated = lambda: print("LED off")
```

#### Context Manager

```python
with LED(17) as led:
    led.on()
    time.sleep(1)
# Automatically cleaned up
```

---

### Type Hints

Enhanced with type hints:

```python
from typing import Optional
from gpiozero import LED

green: LED
yellow: LED
red: LED

def set_led(color: Optional[str]) -> None:
    """Set LED to specified color."""
    ...

def selftest() -> None:
    """Run LED self-test."""
    ...
```

---

### Configuration

#### Pin Configuration

Update pin numbers to match your wiring:

```python
# actors/led.py
from gpiozero import LED

# Configure GPIO pins
green = LED(17)   # GPIO 17 (Physical pin 11)
yellow = LED(27)  # GPIO 27 (Physical pin 13)
red = LED(22)     # GPIO 22 (Physical pin 15)
```

#### Alternative Pins

If using different GPIO pins:

```python
# Custom pin configuration
LED_PINS = {
    'green': 23,
    'yellow': 24,
    'red': 25
}

green = LED(LED_PINS['green'])
yellow = LED(LED_PINS['yellow'])
red = LED(LED_PINS['red'])
```

#### Configuration File

For better maintainability:

```python
# config.py
LED_CONFIG = {
    'green': {'pin': 17, 'active_high': True},
    'yellow': {'pin': 27, 'active_high': True},
    'red': {'pin': 22, 'active_high': True}
}

# actors/led.py
from config import LED_CONFIG

green = LED(LED_CONFIG['green']['pin'])
yellow = LED(LED_CONFIG['yellow']['pin'])
red = LED(LED_CONFIG['red']['pin'])
```

---

### Error Handling

#### GPIO Errors

```python
import actors.led
from gpiozero import GPIOPinInUse, BadPinFactory

try:
    actors.led.set_led("green")

except GPIOPinInUse:
    print("Error: GPIO pin already in use")
    print("Solution: Release pin or use different pin")

except BadPinFactory:
    print("Error: Invalid pin factory")
    print("Solution: Check gpiozero installation")

except Exception as e:
    print(f"Unexpected error: {e}")
```

#### Safe LED Control

```python
def safe_set_led(color):
    """Set LED with error handling"""
    try:
        actors.led.set_led(color)
        return True
    except Exception as e:
        print(f"LED control failed: {e}")
        return False

success = safe_set_led("green")
if not success:
    print("Using fallback behavior")
```

---

### Testing

#### Unit Test Example

```python
import unittest
from unittest.mock import Mock, patch, call
import actors.led

class TestLEDController(unittest.TestCase):

    @patch('actors.led.LED')
    def test_set_led_green(self, mock_led):
        """Test green LED activation"""
        actors.led.set_led("green")

        # Verify all LEDs turned off first
        actors.led.green.off.assert_called()
        actors.led.yellow.off.assert_called()
        actors.led.red.off.assert_called()

        # Verify green turned on
        actors.led.green.on.assert_called_once()

    def test_set_led_invalid(self):
        """Test invalid color turns all off"""
        actors.led.set_led("invalid")

        # All should be off, none on
        self.assertEqual(actors.led.green.on.call_count, 0)
        self.assertEqual(actors.led.yellow.on.call_count, 0)
        self.assertEqual(actors.led.red.on.call_count, 0)

    @patch('actors.led.sleep')
    def test_selftest_sequence(self, mock_sleep):
        """Test self-test runs correct sequence"""
        actors.led.selftest()

        # Verify sleep called 3 times
        self.assertEqual(mock_sleep.call_count, 3)

if __name__ == '__main__':
    unittest.main()
```

---

### Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| `set_led()` | < 1ms | Single color change |
| `selftest()` | 3000ms | Fixed duration (3 × 1s) |
| GPIO write | < 100μs | Hardware operation |
| LED response | < 1ms | Physical LED activation |

---

### Related Documentation

- **[LED Controller Guide](../actors/led.md)** - Detailed LED documentation
- **[Actors Overview](../actors/index.md)** - All actors documentation
- **[Hardware Wiring](../hardware/wiring.md)** - Connection guide
- **[gpiozero LED Docs](https://gpiozero.readthedocs.io/en/stable/api_output.html#led)** - Library reference
