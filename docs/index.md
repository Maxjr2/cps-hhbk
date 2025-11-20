# CPS HHBK Temperature Monitoring System

Welcome to the documentation for the CPS HHBK project - a Cyber-Physical System (CPS) designed for temperature monitoring and visual feedback using Raspberry Pi.

## Overview

This project implements an intelligent temperature monitoring system that reads ambient temperature using a KY-001 sensor (DS18B20) and provides visual feedback through RGB LEDs based on configurable temperature thresholds.

### Key Features

- **Real-time Temperature Monitoring**: Continuous temperature reading using the KY-001 (DS18B20) sensor
- **Visual Feedback System**: Color-coded LED indicators for different temperature ranges
- **Modular Architecture**: Clean separation between sensors, actors, and application logic
- **Raspberry Pi Based**: Designed to run on Raspberry Pi hardware with GPIO support

### Temperature Ranges

The system categorizes temperature into three zones:

| Temperature Range | LED Color | Status |
|------------------|-----------|--------|
| < 21°C | :green_circle: Green | Cool/Comfortable |
| 21-25°C | :yellow_circle: Yellow | Warm |
| ≥ 26°C | :red_circle: Red | Hot |

!!! info "Project Purpose"
    This project was developed as part of Block 2 CPS coursework at HHBK, demonstrating practical application of cyber-physical systems concepts including sensor integration, actuator control, and embedded systems programming.

## Quick Start

To get started with the CPS HHBK system:

1. **[Getting Started](getting-started.md)** - Installation and setup instructions
2. **[Hardware Setup](hardware/overview.md)** - Connect your sensors and LEDs
3. **[Architecture](architecture/how-it-works.md)** - Understand how the system works

## Project Structure

```
cps-hhbk/
├── sensors/          # Sensor modules for data acquisition
│   ├── ky001.py     # KY-001 temperature sensor driver
│   └── sensors.py   # Base sensor abstractions
├── actors/          # Actor modules for output control
│   ├── led.py       # LED controller
│   └── actors.py    # Base actor abstractions
├── main.py          # Main application logic
├── tests/           # Unit tests
└── docs/            # Project documentation
```

## Documentation Sections

### :rocket: [Getting Started](getting-started.md)
Installation instructions, dependencies, and initial setup guide.

### :material-chip: [Architecture](architecture/how-it-works.md)
Learn about the system architecture, design patterns, and how components interact.

### :material-developer-board: [Hardware Setup](hardware/overview.md)
Detailed hardware wiring diagrams and component specifications.

### :material-thermometer: [Sensors](sensors/index.md)
Documentation for all sensor modules including the KY-001 temperature sensor.

### :material-led-on: [Actors](actors/index.md)
Documentation for all actor modules including LED controllers.

### :material-code-braces: [API Reference](api/sensors.md)
Complete API documentation for sensors and actors.

### :material-wrench: [Troubleshooting](troubleshooting.md)
Common issues and solutions.

## Technology Stack

- **Python 3**: Primary programming language
- **gpiozero**: GPIO interface library for Raspberry Pi
- **1-Wire Protocol**: For DS18B20 temperature sensor communication
- **Raspberry Pi**: Hardware platform

## Contributing

This is an educational project. For questions or contributions, please refer to the [GitHub repository](https://github.com/Maxjr2/cps-hhbk).

## License

This project is part of academic coursework at HHBK.