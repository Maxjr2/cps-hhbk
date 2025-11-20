# Hardware Setup Overview

This guide covers the physical setup of the CPS HHBK temperature monitoring system.

## Required Components

### Core Components

| Component | Quantity | Specification | Purpose |
|-----------|----------|---------------|---------|
| Raspberry Pi | 1 | Pi 3/4/Zero W | Main controller |
| KY-001 Sensor | 1 | DS18B20 based | Temperature sensing |
| Green LED | 1 | 5mm, 2.0V forward voltage | Cool indicator |
| Yellow LED | 1 | 5mm, 2.0V forward voltage | Warm indicator |
| Red LED | 1 | 5mm, 1.8V forward voltage | Hot indicator |
| 220Ω Resistor | 3 | 1/4W | LED current limiting |
| 4.7kΩ Resistor | 1 | 1/4W | 1-Wire pull-up |

### Additional Materials

- **Breadboard** (at least 400 tie points)
- **Jumper wires** (male-to-male and male-to-female)
- **Power supply** for Raspberry Pi (5V, 2.5A minimum)
- **MicroSD card** (8GB+) with Raspberry Pi OS

!!! tip "Component Alternatives"
    - Any DS18B20-based sensor works (waterproof, bare chip, etc.)
    - LED colors can be customized to preference
    - Resistor values can be adjusted based on LED specifications

## Component Specifications

### KY-001 Temperature Sensor

**Based on DS18B20 Digital Temperature Sensor**

| Parameter | Specification |
|-----------|--------------|
| Operating Voltage | 3.0V - 5.5V |
| Temperature Range | -55°C to +125°C |
| Accuracy | ±0.5°C (-10°C to +85°C) |
| Resolution | 9 to 12 bits (configurable) |
| Interface | 1-Wire (Dallas/Maxim) |
| Conversion Time | 750ms (12-bit resolution) |

**Pinout:**

```
KY-001 Sensor
┌─────────────┐
│     [S]     │  Signal/Data
│     [+]     │  VCC (3.3V)
│     [-]     │  GND
└─────────────┘
```

### LEDs

Standard 5mm LEDs with the following typical specifications:

| LED Color | Forward Voltage | Forward Current | Wavelength |
|-----------|----------------|-----------------|------------|
| Green | 2.0 - 2.2V | 20mA | 520-570nm |
| Yellow | 2.0 - 2.2V | 20mA | 585-595nm |
| Red | 1.8 - 2.0V | 20mA | 620-700nm |

**LED Pinout:**
```
    LED
    ┌─┐
   ─┤ ├─  Longer leg = Anode (+)
    └─┘   Shorter leg = Cathode (-)
```

### Raspberry Pi GPIO

The Raspberry Pi provides:

- **3.3V GPIO pins** for digital I/O
- **5V and 3.3V power pins** for components
- **Ground pins** for circuit completion
- **Special function pins** including GPIO 4 for 1-Wire

!!! warning "Voltage Warning"
    Raspberry Pi GPIO pins are **3.3V only**. Do not connect 5V signals directly to GPIO pins without level shifters!

## GPIO Pin Assignments

### Recommended Pin Configuration

| Component | GPIO Pin | Physical Pin | Function |
|-----------|----------|--------------|----------|
| KY-001 Data | GPIO 4 | Pin 7 | 1-Wire data |
| Green LED | GPIO 17 | Pin 11 | Digital output |
| Yellow LED | GPIO 27 | Pin 13 | Digital output |
| Red LED | GPIO 22 | Pin 15 | Digital output |
| 3.3V Power | 3.3V | Pin 1 or 17 | Power supply |
| Ground | GND | Pin 6, 9, 14, 20 | Common ground |

### Pin Diagram

```
Raspberry Pi GPIO Header (Top View)
     3.3V [ 1] [ 2] 5V
          [ 3] [ 4] 5V
          [ 5] [ 6] GND
   GPIO 4 [ 7] [ 8]
      GND [ 9] [10]
 GPIO 17  [11] [12]
 GPIO 27  [13] [14] GND
 GPIO 22  [15] [16]
     3.3V [17] [18]
          [19] [20] GND
          ... (continues)
```

!!! info "GPIO Numbering"
    We use **BCM (Broadcom) GPIO numbering**, not physical pin numbers. Make sure your code uses BCM mode:
    ```python
    from gpiozero import LED
    # gpiozero uses BCM numbering by default
    green = LED(17)  # GPIO 17, not pin 17
    ```

## Power Requirements

### System Power Budget

| Component | Voltage | Current Draw | Power |
|-----------|---------|--------------|-------|
| Raspberry Pi 3B+ | 5V | ~500mA idle, 1A active | 2.5-5W |
| KY-001 Sensor | 3.3V | ~1mA | ~3mW |
| Green LED | 3.3V | 20mA | ~40mW |
| Yellow LED | 3.3V | 20mA | ~40mW |
| Red LED | 3.3V | 20mA | ~40mW |
| **Total** | **5V** | **~550-1050mA** | **~2.6-5.2W** |

!!! warning "Power Supply Sizing"
    Use a quality 5V/2.5A (minimum) power supply for Raspberry Pi 3/4. Underpowered supplies cause stability issues, corrupted SD cards, and random reboots.

### LED Current Limiting

Calculate resistor values for safe LED operation:

```
R = (Vsupply - Vled) / Iled

For 3.3V supply and green LED (Vf = 2.0V):
R = (3.3V - 2.0V) / 0.02A = 65Ω

Use standard 220Ω for all LEDs (safer, dimmer)
Actual current: I = (3.3V - 2.0V) / 220Ω ≈ 6mA
```

!!! tip "Resistor Selection"
    - **220Ω**: Safe, dimmer LEDs (~6-8mA)
    - **150Ω**: Brighter LEDs (~10-12mA)
    - **100Ω**: Maximum brightness (~15-18mA)

## Environmental Considerations

### Operating Environment

| Parameter | Recommendation | Notes |
|-----------|----------------|-------|
| Ambient Temperature | 0°C to 40°C | Raspberry Pi safe range |
| Humidity | 20% to 80% RH | Non-condensing |
| Ventilation | Required | Passive cooling adequate |
| Enclosure | Recommended | Protection from dust/moisture |
| Sensor Placement | Away from heat sources | Avoid direct sun, heat vents |

### Sensor Placement Guidelines

**Do:**
- ✅ Place in free air for ambient temperature measurement
- ✅ Keep away from Raspberry Pi (heat generation)
- ✅ Use cable extension if needed (1-Wire supports long cables)
- ✅ Mount at desired measurement height

**Don't:**
- ❌ Place near heat-generating components
- ❌ Expose to direct sunlight
- ❌ Mount in enclosed spaces without ventilation
- ❌ Place directly on metal surfaces (thermal coupling)

## Safety Considerations

### Electrical Safety

!!! danger "Important Safety Rules"
    1. **Power off** before making connections
    2. **Check polarity** of all components
    3. **Verify voltage levels** (3.3V vs 5V)
    4. **Use current-limiting resistors** for all LEDs
    5. **Avoid short circuits** between power and ground
    6. **Don't hot-swap** sensors or components

### ESD Protection

- Use anti-static wrist strap when handling Raspberry Pi
- Ground yourself before touching components
- Store components in anti-static bags
- Work on non-static surface

### Thermal Management

- Ensure adequate airflow around Raspberry Pi
- Consider heatsinks for Pi 3/4 under continuous operation
- Monitor CPU temperature: `vcgencmd measure_temp`
- Shutdown if temperature exceeds 80°C

## Next Steps

Once you understand the hardware requirements:

1. **[Wiring Guide](wiring.md)** - Step-by-step connection instructions
2. **[Getting Started](../getting-started.md)** - Software setup
3. **[Troubleshooting](../troubleshooting.md)** - Hardware issues and solutions

## Additional Resources

- [Raspberry Pi Pinout Reference](https://pinout.xyz/)
- [DS18B20 Datasheet](https://www.maximintegrated.com/en/products/sensors/DS18B20.html)
- [gpiozero Documentation](https://gpiozero.readthedocs.io/)
- [1-Wire Protocol Overview](https://www.maximintegrated.com/en/design/technical-documents/tutorials/1/1796.html)
