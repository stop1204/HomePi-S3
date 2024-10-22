import pigpio
import time
# Set up pigpio
pi = pigpio.pi()

# Define the button_pin = BCM 22/27  led_pin = 13
btn1_pin = 27 # BCM 27 BOARD 13
btn2_pin = 22 # BCM 22 BOARD 15
led_pin = 13  # BCM 13 BOARD 33
#interrupt handler when button pressed
def button_callback(gpio, level, tick):

    if level == 1:  # Button released (rising edge)
        pi.write(led_pin, 0)
        print("Button released!")
    elif level == 0:  # Button pressed (falling edge)
        pi.write(led_pin, 1)
        print("Button pressed!")
#interrupt handler when button 1 pressed
def my_callback(gpio, level, tick):
    if level == 0:  # Falling edge detected
        print ("falling edge detected on button 1")
        pi.write(led_pin, 1)  # Turn on LED

#interrupt handler when button 2 pressed
def my_callback2(gpio, level, tick):
    if level == 0:  # Falling edge detected
        print ("falling edge detected on button 2")
        pi.write(led_pin, 0)  # Turn off LED

pi.set_mode(led_pin, pigpio.OUTPUT)
pi.write(led_pin, 0)

pi.set_mode(btn1_pin, pigpio.INPUT)
pi.set_pull_up_down(btn1_pin, pigpio.PUD_UP)

pi.set_mode(btn2_pin, pigpio.INPUT)
pi.set_pull_up_down(btn2_pin, pigpio.PUD_UP)
pi.callback(btn1_pin, pigpio.FALLING_EDGE, my_callback)
pi.callback(btn2_pin, pigpio.FALLING_EDGE, my_callback2)

try:
    while True:
        pi.write(led_pin, 1)
        time.sleep(0.5)
        pi.write(led_pin, 0)
        time.sleep(0.5)

except KeyboardInterrupt:
    # GPIO.cleanup()
    print("Exiting...")
finally:
    pi.stop()  # Clean up when the program exits