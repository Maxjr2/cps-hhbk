# How It Works

This page explains the operational flow and logic of the CPS HHBK temperature monitoring system.

## System Overview

The CPS HHBK system is a simple yet effective cyber-physical system that bridges the physical world (temperature) with digital control (LED indicators). It operates in a continuous sense-decide-act loop.

```mermaid
graph LR
    A[KY-001 Sensor] -->|Temperature Data| B[Main Controller]
    B -->|Control Signal| C[LED Actors]
    C -->|Visual Feedback| D[User/Environment]
    D -.->|Heat/Cool| A
```

## Operational Flow

### 1. Temperature Sensing

The system continuously reads temperature from the KY-001 sensor via the 1-Wire protocol:

```mermaid
sequenceDiagram
    participant Main
    participant KY001
    participant Hardware

    Main->>KY001: read_temp()
    KY001->>Hardware: read_temp_raw()
    Hardware-->>KY001: Raw data
    KY001->>KY001: Validate (check YES)
    KY001->>KY001: Parse temperature
    KY001->>KY001: Convert to °C and °F
    KY001-->>Main: (temp_c, temp_f)
```

**Key Steps:**

1. **Raw Data Read**: Opens `/sys/bus/w1/devices/28-*/w1_slave` to read sensor data
2. **Validation**: Checks if the CRC is valid (line ends with "YES")
3. **Retry Logic**: If invalid, waits 200ms and retries
4. **Temperature Extraction**: Parses the temperature value (format: `t=23500` for 23.5°C)
5. **Conversion**: Calculates both Celsius and Fahrenheit values

### 2. Decision Logic

The main controller (`main.py`) implements a threshold-based decision algorithm:

```python
def get_sensor_state():
    temperature = sensors.ky001.read_temp()
    if temperature < 21:
        actors.led.set_led("green")
    elif temperature >= 26:
        actors.led.set_led("yellow")
    elif temperature >= 31:
        actors.led.set_led("red")
```

!!! note "Temperature Thresholds"
    The current implementation has three temperature zones:

    - **Cool Zone** (< 21°C): Green LED
    - **Warm Zone** (21-25°C): Yellow LED
    - **Hot Zone** (≥ 26°C): Red LED

!!! warning "Logic Issue"
    There's a logical issue in the current implementation - the condition `elif temperature >= 31` will never be reached because `elif temperature >= 26` catches all values ≥ 26. This should be reviewed and fixed.

### 3. LED Actuation

The LED controller manages GPIO pins to control LED states:

```mermaid
graph TD
    A[set_led called] --> B[Turn off all LEDs]
    B --> C{Which color?}
    C -->|green| D[Turn on Green GPIO]
    C -->|yellow| E[Turn on Yellow GPIO]
    C -->|red| F[Turn on Red GPIO]
    C -->|None/other| G[All LEDs off]
```

**LED Control Process:**

1. **Reset State**: All LEDs are turned off first
2. **Selective Activation**: Only the target LED is turned on
3. **GPIO Management**: Uses `gpiozero.LED` for clean GPIO abstraction

## Control Loop

### Current Implementation

The current implementation executes a single temperature check followed by a self-test:

```python
# main.py
actors.led.selftest()  # Runs once at startup
```

### Continuous Monitoring (Recommended)

For continuous monitoring, implement a control loop:

```python
import time
from main import get_sensor_state

while True:
    get_sensor_state()
    time.sleep(5)  # Check every 5 seconds
```

```mermaid
graph TD
    Start([Start]) --> Init[Initialize Hardware]
    Init --> SelfTest[Run LED Self-Test]
    SelfTest --> Loop{Monitoring Loop}
    Loop --> ReadTemp[Read Temperature]
    ReadTemp --> Evaluate[Evaluate Threshold]
    Evaluate --> UpdateLED[Update LED State]
    UpdateLED --> Wait[Wait 5 seconds]
    Wait --> Loop
```

## System States

The system can be in one of the following states:

| State | Temperature | LED Status | GPIO State |
|-------|-------------|------------|------------|
| Cool | < 21°C | Green ON | GPIO 17: HIGH |
| Comfortable | 21-25°C | Yellow ON | GPIO 27: HIGH |
| Warm | ≥ 26°C | Red ON | GPIO 22: HIGH |
| Self-Test | N/A | Cycling | Sequential activation |
| Idle | N/A | All OFF | All GPIOs: LOW |

## Error Handling

### Sensor Errors

The `read_temp()` function handles sensor errors through validation:

```python
while lines[0].strip()[-3:] != 'YES':
    time.sleep(0.2)
    lines = read_temp_raw()
```

If the CRC check fails, the system retries indefinitely until a valid reading is obtained.

!!! danger "Infinite Loop Risk"
    If the sensor is disconnected or malfunctioning, this creates an infinite loop. Production code should implement a retry limit and error handling.

### GPIO Errors

GPIO errors (e.g., pin already in use, permission denied) are not currently handled and will cause the program to crash.

## Data Flow

```mermaid
flowchart LR
    subgraph Physical
        Env[Environment]
        Sensor[DS18B20 Sensor]
        LEDs[RGB LEDs]
    end

    subgraph Software
        KY001[ky001.py]
        Main[main.py]
        LED[led.py]
    end

    subgraph Hardware Interface
        OneWire[1-Wire Bus]
        GPIO[GPIO Pins]
    end

    Env -->|Heat Transfer| Sensor
    Sensor <-->|Digital Signal| OneWire
    OneWire <-->|/sys/bus/w1| KY001
    KY001 -->|temp_c, temp_f| Main
    Main -->|Color Command| LED
    LED <-->|gpiozero| GPIO
    GPIO <-->|Electrical Signal| LEDs
    LEDs -->|Light| Env
```

## Performance Characteristics

- **Sensor Update Rate**: ~1-2 readings/second (limited by DS18B20 conversion time)
- **Response Time**: < 1 second from temperature change to LED update
- **Accuracy**: ±0.5°C (DS18B20 specification)
- **Resolution**: 0.001°C (software), 0.0625°C (hardware)

## Next Steps

- **[System Design](system-design.md)** - Architectural patterns and design decisions
- **[API Reference](../api/sensors.md)** - Detailed API documentation
- **[Hardware Setup](../hardware/overview.md)** - Physical implementation details
