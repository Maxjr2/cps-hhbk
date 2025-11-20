"""Actor module to control LEDs."""

from time import sleep
import config

# Try to import real hardware, fall back to mock for testing
try:
    from gpiozero import LED
except (ImportError, RuntimeError):
    # Mock LED class for testing on non-RPi systems
    class LED:
        def __init__(self, pin=None):
            self.pin = pin
            self.state = False

        def on(self):
            self.state = True
            print(f"[MOCK] LED on pin {self.pin}: ON")

        def off(self):
            self.state = False
            print(f"[MOCK] LED on pin {self.pin}: OFF")

# Initialize LED hardware
green_led = LED(config.LED_GREEN_PIN)
yellow_led = LED(config.LED_YELLOW_PIN)
red_led = LED(config.LED_RED_PIN)

# LED mapping for easier access
LEDS = {
    "green": green_led,
    "yellow": yellow_led,
    "red": red_led
}


def set_led(color):
    """Sets the LED color by turning off all LEDs and activating the specified one.

    Args:
        color (str): LED color to activate ('green', 'yellow', or 'red')
    """
    # Turn off all LEDs
    for led in LEDS.values():
        led.off()

    # Turn on requested LED if valid
    if color in LEDS:
        LEDS[color].on()


def selftest():
    """Runs a self-test by cycling through all LED colors."""
    for color in ["green", "yellow", "red"]:
        set_led(color)
        sleep(1)

    # Turn off all LEDs after test
    set_led(None)