import pigpio
import time

# Set up pigpio
pi = pigpio.pi()

# Define the button_pin = BCM 19  led_pin = 13
button_pin = 19
led_pin = 13

#interrupt handler when button pressed
def button_callback(gpio, level, tick):
    # if GPIO.input(btn_pin):
    #     GPIO.output(led_pin, GPIO.LOW)
    # else:
    #     GPIO.output(led_pin, GPIO.HIGH)

    if level == 1:  # Button released (rising edge)
        pi.write(led_pin, 0)
        print("Button released!")
    elif level == 0:  # Button pressed (falling edge)
        pi.write(led_pin, 1)
        print("Button pressed!")

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(btn_pin, GPIO.IN)
# GPIO.setup(led_pin, GPIO.OUT)
# GPIO.output(led_pin, GPIO.LOW)
# Set up the button pin with a pull-up resistor (same as GPIO.PUD_UP)
pi.set_mode(led_pin, pigpio.OUTPUT)
pi.write(led_pin, 0)
pi.set_mode(button_pin, pigpio.INPUT)
pi.set_pull_up_down(button_pin, pigpio.PUD_UP)
#enable interrupt, both rising and falling edge triggered
# GPIO.add_event_detect(btn_pin, GPIO.BOTH,callback=button_callback, bouncetime=250)
pi.callback(button_pin, pigpio.EITHER_EDGE, button_callback)

#main program
# try:
#     while True:
#         pass
# except KeyboardInterrupt:
#     GPIO.cleanup()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    # GPIO.cleanup()
    print("Exiting...")
finally:
    pi.stop()  # Clean up when the program exits