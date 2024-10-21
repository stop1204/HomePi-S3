import pigpio
import time

# Set up pigpio
pi = pigpio.pi()

# Define the pin number (BCM 19)
button_pin = 19

# Callback function for handling the button press
def button_callback(gpio, level, tick):
    if level == 0:  # Button pressed (falling edge)
        print("Button pressed!")
    elif level == 1:  # Button released (rising edge)
        print("Button released!")

# Set up the button pin with a pull-up resistor (same as GPIO.PUD_UP)
pi.set_mode(button_pin, pigpio.INPUT)
pi.set_pull_up_down(button_pin, pigpio.PUD_UP)

# Set up edge detection (callback will trigger on both edges)
pi.callback(button_pin, pigpio.EITHER_EDGE, button_callback)

# Keep the program running
try:
    while True:
        time.sleep(0.1)  # Sleep to prevent high CPU usage
except KeyboardInterrupt:
    print("Exiting...")
finally:
    pi.stop()  # Clean up when the program exits