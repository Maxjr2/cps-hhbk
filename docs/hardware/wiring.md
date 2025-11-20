# Wiring Guide

This guide provides step-by-step instructions for physically connecting all components of the CPS HHBK system.

!!! danger "Safety First"
    **Always power off your Raspberry Pi before making or changing connections!**

## Wiring Overview

```
                    ┌─────────────────────┐
                    │   Raspberry Pi      │
                    │                     │
    KY-001 Sensor ──┤ GPIO 4 (Pin 7)     │
                    │ 3.3V   (Pin 1)     │
                    │ GND    (Pin 6)     │
                    │                     │
     Green LED ─────┤ GPIO 17 (Pin 11)   │
    Yellow LED ─────┤ GPIO 27 (Pin 13)   │
       Red LED ─────┤ GPIO 22 (Pin 15)   │
                    │                     │
       Common ──────┤ GND (Pin 9, 14, 20)│
                    └─────────────────────┘
```

## Step-by-Step Instructions

### Step 1: Prepare Your Workspace

1. **Gather all components** (see [Hardware Overview](overview.md))
2. **Power off Raspberry Pi** and disconnect power supply
3. **Set up breadboard** near the Raspberry Pi
4. **Organize jumper wires** by length and color

!!! tip "Wire Color Convention"
    Use consistent wire colors for easier debugging:
    - **Red**: 3.3V power
    - **Black**: Ground
    - **White/Yellow**: Data/signal lines
    - **Green/Yellow/Red**: Respective LED control signals

### Step 2: Connect Power Rails

Set up power distribution on breadboard:

```
Breadboard Power Rails:
────────────────────────────
  + + + + +  Power Rail (+)
────────────────────────────
  - - - - -  Ground Rail (-)
────────────────────────────
```

**Connections:**

1. Connect Raspberry Pi **Pin 1 (3.3V)** to breadboard **+ power rail** (red wire)
2. Connect Raspberry Pi **Pin 6 (GND)** to breadboard **- ground rail** (black wire)

### Step 3: Wire the KY-001 Temperature Sensor

**Required:**
- KY-001 sensor module
- 4.7kΩ resistor (pull-up resistor)
- 3 jumper wires

**Connections:**

| KY-001 Pin | Connect To | Wire Color | Notes |
|------------|------------|------------|-------|
| VCC (+) | Breadboard + rail | Red | 3.3V power |
| GND (-) | Breadboard - rail | Black | Ground |
| DATA (S) | GPIO 4 (Pin 7) | Yellow | 1-Wire signal |

**Pull-up Resistor:**

Place a 4.7kΩ resistor between:
- One end: DATA line (GPIO 4)
- Other end: 3.3V power rail

```
        3.3V
         │
         ├─── 4.7kΩ resistor
         │
    KY-001 DATA ────── GPIO 4
```

!!! info "Why Pull-up Resistor?"
    The 1-Wire protocol requires a pull-up resistor on the data line. The DS18B20 uses open-drain output, which can only pull the line low. The resistor pulls it high when not driven.

**Physical Layout:**

```
                    KY-001
                   ┌───────┐
              Red  │ VCC   │
           Yellow  │ DATA  │
            Black  │ GND   │
                   └───────┘
                       │ │ │
       4.7kΩ ─────┐    │ │ │
    3.3V ──────────┴────┘ │ │
    GPIO 4 ────────────────┘ │
    GND ───────────────────────┘
```

### Step 4: Wire the LEDs

**Required per LED:**
- 1 LED
- 1 220Ω resistor
- 2 jumper wires

#### LED Orientation

!!! warning "LED Polarity"
    LEDs are polarized - they only work in one direction!

    - **Anode (+)**: Longer leg, connects to GPIO through resistor
    - **Cathode (-)**: Shorter leg, flat side, connects to ground

```
      LED Symbol
         ─┬─
        ──┤├──  Triangle points toward ground
          ┴
    Anode (+)  Cathode (-)
```

#### Green LED Wiring

1. Insert **green LED** into breadboard
2. Connect **longer leg (anode)** to one end of 220Ω resistor
3. Connect **other end of resistor** to **GPIO 17 (Pin 11)**
4. Connect **shorter leg (cathode)** to **ground rail (-)** (black wire)

```
GPIO 17 ────── 220Ω ────┬──▶│──┬──── GND
                            │
                       Green LED
```

#### Yellow LED Wiring

1. Insert **yellow LED** into breadboard
2. Connect **longer leg (anode)** to one end of 220Ω resistor
3. Connect **other end of resistor** to **GPIO 27 (Pin 13)**
4. Connect **shorter leg (cathode)** to **ground rail (-)** (black wire)

```
GPIO 27 ────── 220Ω ────┬──▶│──┬──── GND
                            │
                      Yellow LED
```

#### Red LED Wiring

1. Insert **red LED** into breadboard
2. Connect **longer leg (anode)** to one end of 220Ω resistor
3. Connect **other end of resistor** to **GPIO 22 (Pin 15)**
4. Connect **shorter leg (cathode)** to **ground rail (-)** (black wire)

```
GPIO 22 ────── 220Ω ────┬──▶│──┬──── GND
                            │
                        Red LED
```

### Step 5: Complete Breadboard Layout

**Top view of breadboard:**

```
Power Rails:        Breadboard Layout:

+ ─────────────     GPIO 17 ──┳── 220Ω ──┳──▶│──┬── GND
- ─────────────                            Green

3.3V from Pi        GPIO 27 ──┳── 220Ω ──┳──▶│──┬── GND
                                            Yellow

                    GPIO 22 ──┳── 220Ω ──┳──▶│──┬── GND
                                             Red
KY-001 Module
┌────────┐          GPIO 4 ───┬─────┬── KY-001 DATA
│ VCC    │                    │     │
│ DATA   │          4.7kΩ ────┤     │
│ GND    │                    │     │
└────────┘          3.3V ──────┴─────┴── KY-001 VCC

                    GND ────────────────── KY-001 GND
```

## Connection Verification Checklist

Before powering on, verify:

- [ ] **All power connections** are to 3.3V (not 5V)
- [ ] **All ground connections** are secure
- [ ] **LED polarity** is correct (long leg to resistor/GPIO)
- [ ] **All resistors** are in place (3× 220Ω for LEDs, 1× 4.7kΩ for sensor)
- [ ] **GPIO pins** match the code configuration
- [ ] **No short circuits** between power and ground
- [ ] **KY-001 sensor** connections are correct
- [ ] **Pull-up resistor** is connected for 1-Wire

## Visual Inspection

Perform visual inspection:

1. **Check all connections** are firm
2. **Look for loose wires** on breadboard
3. **Verify wire routing** doesn't cross power/ground
4. **Check for solder bridges** if using permanent connections
5. **Ensure components** are not touching each other

## First Power-On Test

### Safe Power-Up Procedure

1. **Double-check all connections** against this guide
2. **Connect Raspberry Pi power supply** (do not turn on yet)
3. **Verify no smoke or burning smell**
4. **Power on Raspberry Pi**
5. **Watch for boot LED** on Raspberry Pi
6. **Check for unusual behavior**:
   - Immediate shutdown (short circuit)
   - No boot (power issue)
   - Burning smell (stop immediately!)

### Initial Hardware Test

Once booted, test connections:

```bash
# Test 1-Wire sensor detection
ls /sys/bus/w1/devices/

# Should see: 28-XXXXXXXXXXXX (your sensor)
```

```python
# Test LED control
python3
>>> from gpiozero import LED
>>> green = LED(17)
>>> green.on()   # Green LED should light up
>>> green.off()  # Should turn off
```

!!! success "Hardware Ready!"
    If all tests pass, your hardware is correctly wired! Proceed to [Getting Started](../getting-started.md) for software configuration.

## Circuit Diagrams

### Schematic Diagram

```
                     Raspberry Pi
                   ┌──────────────┐
                   │              │
                   │ 3.3V (Pin 1) ├─────┬──────────────┬─────────┐
                   │              │     │              │         │
                   │ GPIO 4  (P7) ├────┬┴──────────┐   │         │
                   │ GPIO 17 (P11)├──┐ │  4.7kΩ    │   │         │
                   │ GPIO 27 (P13)├─┐│ │           │   │         │
                   │ GPIO 22 (P15)├┐││ └───────────┤   │         │
                   │              ││││             KY-001         │
                   │ GND     (P6) ├┼┼┼──────────────┤   │         │
                   │ GND     (P9) ├┼┼┼┐        DATA─┘   │         │
                   │ GND    (P14) ├┼┼││        VCC──────┘         │
                   │ GND    (P20) ├┼┼││        GND───────────────┐│
                   └──────────────┘│││││                          ││
                                   │││││                          ││
    Green LED:  GPIO 17 ────220Ω───┼┼┼│├──▶│───┐                 ││
    Yellow LED: GPIO 27 ────220Ω───┼┼│││──▶│───┤                 ││
    Red LED:    GPIO 22 ────220Ω───┼││││──▶│───┼─────────────────┘│
                                    ││││└────────────────────────┬─┘
                                    ││└┘                         │
                                    └┴──────────────────────────┬┘
                                                                 └─ Common GND
```

### Fritzing-Style Diagram

```
    Raspberry Pi                          Breadboard
   ┌────────────┐
   │ ●       ● │ Pin 1 (3.3V) ─────────── + Power Rail
   │ ○       ○ │                                │
   │ ○       ○ │                                │
   │ ○       ○ │ Pin 6 (GND) ───────────── - Ground Rail
   │ ●       ○ │ Pin 7 (GPIO4) ─────┐           │
   │ ○       ○ │                    │           │
   │ ○       ○ │                    │     [KY-001]
   │ ●       ○ │ Pin 11 (GPIO17)──┐ └───Data  VCC──┘
   │ ●       ○ │ Pin 13 (GPIO27)─┐│        GND────┐
   │ ○       ○ │                 ││                │
   │ ●       ○ │ Pin 15 (GPIO22)┐││                │
   │ ○       ○ │                │││                │
   └────────────┘                │││                │
                                 │││                │
                       ┌─────────┼┼┼────────────────┼─────┐
                       │  220Ω   │││  220Ω   220Ω   │     │
   Green LED:  ────────┼────▶│───┘││  ─▶│──  ─▶│──  │     │
   Yellow LED: ────────┼──────────┘│────┘         │  │     │
   Red LED:    ────────┼───────────┘              │  │     │
                       │                          │  │     │
   Ground:     ────────┴──────────────────────────┴──┴─────┘
```

## Troubleshooting Wiring Issues

### No LED Response

**Check:**
- [ ] LED polarity (flip if needed)
- [ ] GPIO pin numbers in code match wiring
- [ ] Resistor is present (not blown)
- [ ] Connections are firm
- [ ] Ground connection is secure

### Sensor Not Detected

**Check:**
- [ ] 1-Wire enabled in `raspi-config`
- [ ] 4.7kΩ pull-up resistor is present
- [ ] Data wire connected to GPIO 4
- [ ] Power (3.3V) is connected
- [ ] Ground is connected
- [ ] No reversed polarity on sensor

### Raspberry Pi Won't Boot

**Check:**
- [ ] Power supply is adequate (2.5A+)
- [ ] No short circuit between 3.3V and GND
- [ ] Remove all connections and test Pi alone
- [ ] SD card is properly inserted

## Next Steps

With hardware complete:

1. **[Getting Started](../getting-started.md)** - Configure software
2. **[Troubleshooting](../troubleshooting.md)** - Solve common issues
3. **[API Reference](../api/actors.md)** - Understand the code

## Additional Resources

- [Interactive Raspberry Pi Pinout](https://pinout.xyz/)
- [Breadboard Basics Tutorial](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard)
- [LED Resistor Calculator](https://www.digikey.com/en/resources/conversion-calculators/conversion-calculator-led-series-resistor)
