import RPi.GPIO as GPIO
import time
btn1_pin = 13 # BCM 27
btn2_pin = 15 # BCM 22
led_pin = 33  # BCM 13
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(btn1_pin, GPIO.IN)
GPIO.setup(btn2_pin, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, GPIO.LOW)

#interrupt handler when button 1 pressed
def my_callback(channel):
    print ("falling edge detected on button 1")
#interrupt handler when button 2 pressed
def my_callback2(channel):
    print ("falling edge detected on button 2")
#enable interrupt, falling edge triggered
GPIO.add_event_detect(btn1_pin, GPIO.FALLING, callback=my_callback, bouncetime=300)
GPIO.add_event_detect(btn2_pin, GPIO.FALLING, callback=my_callback2, bouncetime=300)
#main program
try:
    while True: #main loop to blink the LED
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
