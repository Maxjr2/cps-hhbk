from gpiozero import PWMOutputDevice

# The output pin to which the buzzer is connected is declared here.
buzzer = PWMOutputDevice(6, frequency=500, initial_value=0.5)

def buzz_on():
    """Turn the buzzer on."""
    buzzer.value = 0.5

def buzz_off():
    """Turn the buzzer off."""
    buzzer.value = 0.0