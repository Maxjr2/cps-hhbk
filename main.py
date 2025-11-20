"""Main application for temperature monitoring and control."""
import sensor.ky001
import actor.led
import actor.ky006
import config

def get_sensor_state():
    """Reads temperature and controls LED and buzzer based on thresholds."""
    temperature, _ = sensor.ky001.read_temp()

    # Control LED based on temperature ranges
    if temperature < config.TEMP_WARM:
        actor.led.set_led("green")
    elif temperature < config.TEMP_HOT:
        actor.led.set_led("yellow")
    else:
        actor.led.set_led("red")

    # Control buzzer for critical temperatures
    if temperature >= config.TEMP_CRITICAL:
        actor.ky006.buzz("start")
    else:
        actor.ky006.buzz("stop")



def run_selftests():
    """Runs self-tests for all connected sensors and actors."""
    actor.led.selftest()
    actor.ky006.selftest()
    sensor.ky001.selftest()
