"""Actor module to control LEDs."""

from time import sleep
from gpiozero import LED

#TODO implement a better way to handle pins (maybe a config file?)
green = LED()
yellow = LED()
red = LED()

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

def selftest():
    """Runs a self-test by cycling through the LED colors."""
    set_led("green")
    sleep(1)
    set_led("yellow")
    sleep(1)
    set_led("red")
    sleep(1)
    set_led(None)