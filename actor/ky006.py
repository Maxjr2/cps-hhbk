"""KY-006 Buzzer Actor Module."""
from time import sleep
import config

# Try to import real hardware, fall back to mock for testing
try:
    from gpiozero import PWMOutputDevice
except (ImportError, RuntimeError):
    # Mock PWMOutputDevice for testing on non-RPi systems
    class PWMOutputDevice:
        def __init__(self, pin, frequency=500, initial_value=0):
            self.pin = pin
            self.frequency = frequency
            self.value = initial_value

        def __setattr__(self, name, val):
            object.__setattr__(self, name, val)
            if name == "value" and val > 0:
                print(f"[MOCK] Buzzer on pin {self.pin}: BUZZING at {self.frequency}Hz")
            elif name == "value" and val == 0:
                print(f"[MOCK] Buzzer on pin {self.pin}: SILENT")

# Initialize buzzer hardware with configured pin and frequency
buzzer = PWMOutputDevice(
    config.BUZZER_PIN,
    frequency=config.BUZZER_FREQUENCY,
    initial_value=0
)

# Buzzer duty cycle constant
BUZZER_DUTY_CYCLE = 0.5


def buzz(action):
    """Controls the buzzer state.

    Args:
        action (str): 'start' to activate buzzer, 'stop' to deactivate
    """
    if action == "start":
        buzzer.value = BUZZER_DUTY_CYCLE
    elif action == "stop":
        buzzer.value = 0


def selftest():
    """Runs a self-test by activating buzzer briefly."""
    buzz("start")
    sleep(1)
    buzz("stop")