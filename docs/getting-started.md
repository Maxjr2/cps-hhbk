# Getting Started

This guide will help you set up and run the CPS HHBK temperature monitoring system on your Raspberry Pi.

## Prerequisites

### Hardware Requirements

- **Raspberry Pi** (tested on Pi 3/4/Zero W)
- **KY-001 Temperature Sensor** (DS18B20 based)
- **3x LEDs** (Green, Yellow, Red)
- **3x 220Ω Resistors** (for LEDs)
- **Breadboard and jumper wires**
- **Power supply** for Raspberry Pi

### Software Requirements

- Raspberry Pi OS (formerly Raspbian)
- Python 3.7 or higher
- Internet connection for initial setup

!!! warning "GPIO Access Required"
    This project requires GPIO access. Ensure your user is in the `gpio` group:
    ```bash
    sudo usermod -a -G gpio $USER
    ```

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Maxjr2/cps-hhbk.git
cd cps-hhbk
```

### Step 2: Install Python Dependencies

Install the required Python packages:

```bash
pip3 install gpiozero
```

!!! tip "Virtual Environment"
    It's recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install gpiozero
    ```

### Step 3: Enable 1-Wire Interface

The KY-001 sensor uses the 1-Wire protocol. Enable it on your Raspberry Pi:

=== "Using raspi-config"

    ```bash
    sudo raspi-config
    ```

    Navigate to: **Interface Options** → **1-Wire** → **Enable**

=== "Manual Configuration"

    Edit `/boot/config.txt`:
    ```bash
    sudo nano /boot/config.txt
    ```

    Add the following line:
    ```
    dtoverlay=w1-gpio
    ```

    Reboot your Raspberry Pi:
    ```bash
    sudo reboot
    ```

### Step 4: Verify 1-Wire Setup

After reboot, verify the 1-Wire interface is working:

```bash
ls /sys/bus/w1/devices/
```

You should see a device starting with `28-` (your temperature sensor).

!!! failure "Troubleshooting"
    If you don't see the device, check your wiring and ensure the 1-Wire module is loaded:
    ```bash
    lsmod | grep w1
    ```

## Hardware Setup

Before running the software, you need to wire up the components. See the [Hardware Setup Guide](hardware/overview.md) for detailed wiring instructions.

### Quick Wiring Reference

**KY-001 Temperature Sensor:**

- VCC → 3.3V
- GND → Ground
- DATA → GPIO 4 (default 1-Wire pin)

**LEDs (with 220Ω resistors):**

- Green LED → GPIO 17
- Yellow LED → GPIO 27
- Red LED → GPIO 22

!!! warning "Update GPIO Pins"
    The current implementation has placeholder GPIO pins. You'll need to update `actors/led.py` with your actual pin numbers:
    ```python
    green = LED(17)
    yellow = LED(27)
    red = LED(22)
    ```

## Running the Application

### First Run: Self-Test

The application includes a self-test that cycles through all LED colors:

```bash
python3 main.py
```

You should see the LEDs cycle through green → yellow → red → off.

### Normal Operation

To run the temperature monitoring system:

```python
# In main.py or Python shell
from main import get_sensor_state
get_sensor_state()
```

The LED will change based on the current temperature reading.

## Verification

### Test Temperature Sensor

You can manually read the temperature:

```bash
cat /sys/bus/w1/devices/28-*/w1_slave
```

Or using Python:

```python
python3
>>> import sensors.ky001 as temp
>>> temp_c, temp_f = temp.read_temp()
>>> print(f"Temperature: {temp_c}°C / {temp_f}°F")
```

### Test LEDs

Test individual LED control:

```python
python3
>>> import actors.led as led
>>> led.set_led("green")   # Should turn on green LED
>>> led.set_led("yellow")  # Should turn on yellow LED
>>> led.set_led("red")     # Should turn on red LED
>>> led.selftest()         # Cycles through all colors
```

## Next Steps

- **[Architecture Overview](architecture/how-it-works.md)** - Understand how the system works
- **[Hardware Setup Details](hardware/overview.md)** - Detailed wiring diagrams
- **[API Reference](api/sensors.md)** - Explore the codebase
- **[Troubleshooting](troubleshooting.md)** - Solutions to common issues

!!! success "Ready to Go!"
    Once all LEDs respond correctly and temperature readings are accurate, your system is ready for deployment!