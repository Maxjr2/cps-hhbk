"""KY-006 Buzzer Actor Module."""
from time import sleep
from gpiozero import PWMOutputDevice

# The output pin to which the buzzer is connected is declared here.
#TODO implement a better way to handle pins (maybe a config file?)
buzzer = PWMOutputDevice(24, frequency=500, initial_value=0.5)


def buzz(action):
    """Starts or stops the buzzer based on the action parameter."""
    if action == "start":
        buzzer.value = 0.5  # Start buzzing at 50% duty cycle
    elif action == "stop":
        buzzer.value = 0  # Stop buzzing

def selftest():
    """Runs a self-test by buzzing for a short duration."""
    buzz("start")
    sleep(1)
    buzz("stop")







# The program waits for the user to enter a new PWM frequency.
# Until then, the buzzer is operated at the previously entered frequency (starting value 500Hz)
#try:
#    while True:
#        print("----------------------------------------")
#        aktuelle_frequenz = buzzer.frequency
#        print(f"Current frequency: {aktuelle_frequenz:.0f}")
#        neue_frequenz = int(input("Please enter a new frequency (50-5000): "))
#        buzzer.frequency = neue_frequenz
#         
# Clean-up work after the program has been completed
#except KeyboardInterrupt:
#    buzzer.close()
#    print("Program ended")
#