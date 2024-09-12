# run on Pi
import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)


led_pin = 17


GPIO.setup(led_pin, GPIO.OUT)

GPIO.output(led_pin, GPIO.HIGH)
time.sleep(5)


GPIO.output(led_pin, GPIO.LOW)

GPIO.cleanup()