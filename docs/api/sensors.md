# Sensors API Reference

Complete API documentation for all sensor modules in the CPS HHBK system.

## Module: `sensors.ky001`

Temperature sensor module for the KY-001 (DS18B20) digital thermometer.

**Module Path:** `sensors/ky001.py`

**Import:**
```python
import sensors.ky001
from sensors import ky001
```

### Module-Level Variables

#### `base_dir`

Base directory for 1-Wire devices.

**Type:** `str`

**Value:** `'/sys/bus/w1/devices/'`

**Description:** Linux sysfs path where 1-Wire devices are exposed.

**Usage:**
```python
print(sensors.ky001.base_dir)
# /sys/bus/w1/devices/
```

---

#### `device_folder`

Path to the specific DS18B20 device directory.

**Type:** `str`

**Value:** Auto-detected (first device matching `28-*`)

**Description:** Full path to the sensor device folder. The `28-` prefix indicates DS18B20 family code.

**Usage:**
```python
print(sensors.ky001.device_folder)
# /sys/bus/w1/devices/28-0000091234567
```

**Auto-Detection:**
```python
device_folder = glob.glob(base_dir + '28*')[0]
```

!!! warning "Multiple Sensors"
    If multiple DS18B20 sensors are connected, this selects only the first one. Modify code to support multiple sensors.

---

#### `device_file`

Full path to the sensor data file.

**Type:** `str`

**Value:** `{device_folder}/w1_slave`

**Description:** The actual file read to obtain temperature data.

**Usage:**
```python
print(sensors.ky001.device_file)
# /sys/bus/w1/devices/28-0000091234567/w1_slave
```

---

### Functions

#### `read_temp_raw()`

Read raw data from the temperature sensor file.

**Signature:**
```python
def read_temp_raw() -> list[str]
```

**Parameters:**
- None

**Returns:**
- `list[str]`: List of two strings containing raw sensor data

**Return Value Format:**
```python
[
    'f0 01 4b 46 7f ff 0c 10 5c : crc=5c YES\n',
    'f0 01 4b 46 7f ff 0c 10 5c t=31000\n'
]
```

**Line 1:** CRC validation result (ends with `YES` or `NO`)
**Line 2:** Temperature data (format: `t=<temp in millidegrees>`)

**Raises:**
- `FileNotFoundError`: If sensor device file doesn't exist
- `PermissionError`: If insufficient permissions to read file
- `OSError`: On other I/O errors

**Example:**
```python
lines = sensors.ky001.read_temp_raw()
print(lines[0])  # CRC check line
print(lines[1])  # Temperature data line
```

**Implementation Details:**
```python
def read_temp_raw():
    """Reads the raw temperature data from the sensor."""
    f = open(device_file, mode='r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    return lines
```

**Note:** File is opened and closed each time. Consider using `with` statement for better resource management.

---

#### `read_temp()`

Read and process temperature with validation.

**Signature:**
```python
def read_temp() -> tuple[float, float]
```

**Parameters:**
- None

**Returns:**
- `tuple[float, float]`: Temperature as `(celsius, fahrenheit)`
  - Index 0: Temperature in degrees Celsius
  - Index 1: Temperature in degrees Fahrenheit

**Return Value Example:**
```python
(23.5, 74.3)  # 23.5°C, 74.3°F
```

**Raises:**
- `FileNotFoundError`: If sensor is not connected
- `IndexError`: If sensor data format is unexpected
- `ValueError`: If temperature cannot be parsed
- May hang indefinitely if CRC never validates

**Example:**
```python
# Get both units
temp_c, temp_f = sensors.ky001.read_temp()
print(f"Temperature: {temp_c}°C ({temp_f}°F)")

# Get only Celsius
temp_c = sensors.ky001.read_temp()[0]

# Get only Fahrenheit
temp_f = sensors.ky001.read_temp()[1]
```

**Algorithm:**

1. Read raw sensor data
2. Validate CRC (check for 'YES')
3. If invalid, wait 200ms and retry (infinite loop!)
4. Parse temperature value from second line
5. Convert from millidegrees to degrees
6. Calculate Fahrenheit equivalent
7. Return tuple

**Implementation:**
```python
def read_temp():
    """Uses the read_temp_raw function to get the temperature in Celsius and Fahrenheit."""
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
```

**Conversion Formulas:**

```python
# Millidegrees to Celsius
temp_c = raw_value / 1000.0

# Celsius to Fahrenheit
temp_f = temp_c * 9.0 / 5.0 + 32.0

# Or equivalently
temp_f = (temp_c * 1.8) + 32.0
```

**Known Issues:**

!!! danger "Infinite Loop Risk"
    The validation loop has no timeout:
    ```python
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    ```

    If sensor is disconnected or malfunctioning, this will hang forever!

**Improved Version:**

```python
def read_temp_safe(max_retries=10):
    """Read temperature with timeout protection"""
    lines = read_temp_raw()
    attempts = 0

    while lines[0].strip()[-3:] != 'YES':
        if attempts >= max_retries:
            raise TimeoutError("Sensor CRC validation failed")
        time.sleep(0.2)
        lines = read_temp_raw()
        attempts += 1

    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    else:
        raise ValueError("Temperature value not found in sensor data")
```

---

### Data Formats

#### Raw Sensor Output

**Format:**
```
<hex bytes> : crc=<crc_value> <YES|NO>
<hex bytes> t=<temperature>
```

**Example:**
```
f0 01 4b 46 7f ff 0c 10 5c : crc=5c YES
f0 01 4b 46 7f ff 0c 10 5c t=31000
```

**Parsing:**

```python
# Line 1: CRC validation
is_valid = lines[0].strip().endswith('YES')

# Line 2: Temperature extraction
if 't=' in lines[1]:
    start = lines[1].index('t=') + 2
    temp_string = lines[1][start:].strip()
    temp_millidegrees = int(temp_string)
    temp_celsius = temp_millidegrees / 1000.0
```

#### Temperature Encoding

Temperature is stored as signed 16-bit integer in millidegrees Celsius:

| Raw Value | Temperature | Notes |
|-----------|-------------|-------|
| 23500 | 23.5°C | Positive temperature |
| -10250 | -10.25°C | Negative temperature |
| 0 | 0°C | Freezing point |
| 85000 | 85°C | Power-on reset value |

**Range:** -55000 to 125000 (-55°C to +125°C)

**Resolution:** 0.001°C (software), 0.0625°C (hardware at 12-bit)

---

### Usage Examples

#### Basic Temperature Reading

```python
import sensors.ky001

temp_c, temp_f = sensors.ky001.read_temp()
print(f"Current temperature: {temp_c:.1f}°C / {temp_f:.1f}°F")
```

#### Continuous Monitoring

```python
import time
import sensors.ky001

while True:
    temp_c, temp_f = sensors.ky001.read_temp()
    print(f"{temp_c:.2f}°C", end='\r')
    time.sleep(1)
```

#### Temperature Logging

```python
import sensors.ky001
import time
from datetime import datetime

def log_temperature(interval=60, duration=3600):
    """Log temperature to file every interval seconds for duration seconds"""
    start_time = time.time()

    with open('temp_log.csv', 'w') as f:
        f.write('timestamp,celsius,fahrenheit\n')

        while time.time() - start_time < duration:
            temp_c, temp_f = sensors.ky001.read_temp()
            timestamp = datetime.now().isoformat()
            f.write(f'{timestamp},{temp_c},{temp_f}\n')
            f.flush()
            time.sleep(interval)

log_temperature(interval=10, duration=3600)  # Log every 10s for 1 hour
```

#### With Error Handling

```python
import sensors.ky001
import time

def read_temperature_safe():
    """Safe temperature reading with error handling"""
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            temp_c, temp_f = sensors.ky001.read_temp()

            # Validate reasonable range
            if -50 <= temp_c <= 100:
                return temp_c, temp_f
            else:
                print(f"Unusual temperature: {temp_c}°C")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)

    return None, None

temp_c, temp_f = read_temperature_safe()
if temp_c is not None:
    print(f"Temperature: {temp_c}°C")
else:
    print("Failed to read temperature")
```

#### Temperature Filtering

```python
import sensors.ky001
import time
from statistics import mean

def read_temp_filtered(samples=5, interval=0.2):
    """Read temperature with moving average filter"""
    readings = []

    for _ in range(samples):
        temp_c, _ = sensors.ky001.read_temp()
        readings.append(temp_c)
        time.sleep(interval)

    avg_c = mean(readings)
    avg_f = avg_c * 9.0 / 5.0 + 32.0

    return avg_c, avg_f

# Get filtered reading
temp_c, temp_f = read_temp_filtered(samples=10)
print(f"Filtered temperature: {temp_c:.2f}°C")
```

---

### Error Handling

#### Common Exceptions

```python
import sensors.ky001

try:
    temp_c, temp_f = sensors.ky001.read_temp()

except FileNotFoundError:
    print("Error: Sensor not detected")
    print("Check: 1-Wire enabled? Sensor connected?")

except PermissionError:
    print("Error: Cannot access sensor")
    print("Check: User in gpio group?")

except ValueError as e:
    print(f"Error: Invalid sensor data - {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

#### Timeout Implementation

```python
import sensors.ky001
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Sensor read timeout")

# Set timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)  # 5 second timeout

try:
    temp_c, temp_f = sensors.ky001.read_temp()
    signal.alarm(0)  # Cancel timeout
    print(f"Temperature: {temp_c}°C")

except TimeoutError:
    print("Sensor read timed out - check connections")
```

---

### Type Hints

For better type checking, add type hints:

```python
from typing import Tuple, List

def read_temp_raw() -> List[str]:
    """Read raw temperature data."""
    ...

def read_temp() -> Tuple[float, float]:
    """Read temperature in Celsius and Fahrenheit."""
    ...
```

---

### Related Documentation

- **[KY-001 Sensor Guide](../sensors/sensor-KY001.md)** - Detailed sensor documentation
- **[Hardware Setup](../hardware/wiring.md)** - Wiring instructions
- **[Troubleshooting](../troubleshooting.md)** - Common sensor issues
- **[How It Works](../architecture/how-it-works.md)** - System architecture
