from gpiozero import LED
from time import sleep

red = LED(16)
yellow = LED(20)
green = LED(21)


def set_green(state):
    if state == "on":
        green.on()
    elif state == "off":
        green.off()

def set_yellow(state):
    if state == "on":
        yellow.on()
    elif state == "off":
        yellow.off()

def set_red(state):
    if state == "on":
        red.on()
    elif state == "off":
        red.off()
