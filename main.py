"""...its the main file..."""
import sensors.ky001
import actors.led

def get_sensor_state():
    """Reads the temperature from the KY001 sensor and sets the LED color based on the temperature range."""
    temperature = sensors.ky001.read_temp()
    if temperature < 21:
        actors.led.set_led("green")
    elif temperature >= 26:
        actors.led.set_led("yellow")
    elif temperature >= 31:
        actors.led.set_led("red")



actors.led.selftest()
