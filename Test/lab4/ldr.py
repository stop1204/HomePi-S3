import RPi.GPIO as GPIO
from time import sleep
GPIO.setwarnings(False)
led = 5
light = 3
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led, GPIO.OUT)
def rc_time(pin):
    count = 0
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)
    sleep(0.1)
    GPIO.setup(pin, GPIO.IN)
    while (GPIO.input(pin) == False):
        count += 1
    return count
try:
    while True:
        ldr = rc_time(light)
        print(ldr)
        if ldr > 500:
            GPIO.output(led, True)
        else:
            GPIO.output(led, False)
            sleep(0.5)
finally:
    print("Exit the program...")
    GPIO.cleanup()