# run on Pi
# RPi.GPIO is a Python library that provides a Python interface to the Raspberry Pi GPIO.
# if you want to run this code on macOS, you need to install the RPi.GPIO library.
"""
This Python code controls an LED connected to GPIO pin 17 on a Raspberry Pi.
 It uses the Broadcom (BCM) numbering system, sets pin 17 as an output,
 turns the LED on for 5 seconds, and then turns it off.
 Afterward, it resets the GPIO settings to their default state
 to prevent any issues with lingering signals.
"""
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
led_pin = 17
pwd_led_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(pwd_led_pin, GPIO.OUT)

pwm = GPIO.PWM(pwd_led_pin, 100)
pwm.start(0)
while True:
    GPIO.output(led_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(led_pin, GPIO.LOW)

    for i in range(100):
        pwm.ChangeDutyCycle(i)
        time.sleep(0.01)
    for i in range(100,0,-1):
        pwm.ChangeDutyCycle(i)
        time.sleep(0.01)
GPIO.cleanup()