from gpiozero import LED
from time import sleep

green = LED()
yellow = LED()
red = LED()

def set_led(color):
    green.off()
    yellow.off()
    red.off()
    if color == "green":
        green.on()
    elif color == "yellow":
        yellow.on()
    elif color == "red":
        red.on()

def test_leds():
    set_led("green")
    sleep(1)
    set_led("yellow")
    sleep(1)
    set_led("red")
    sleep(1)
    set_led(None)