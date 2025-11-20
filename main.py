"""...its the main file..."""
import sensor.ky001
import actor.led

#TODO write some better code here /s
def get_sensor_state():
    """Reads temp and sets LED color acordingly. Activates buzzer if temp is too high."""
    temperature = sensor.ky001.read_temp()
    if temperature < 21:
        actor.led.set_led("green")
    elif temperature >= 26:
        actor.led.set_led("yellow")
    elif temperature >= 31:
        actor.led.set_led("red")
        if temperature >= 35:
            actor.ky006.buzz("start")
        elif temperature <= 34:
            actor.ky006.buzz("stop")



def run_selftests():
    """Runs self-tests for all connected sensors and actors."""
    actor.led.selftest()
    actor.ky006.selftest()
    sensor.ky001.selftest()
