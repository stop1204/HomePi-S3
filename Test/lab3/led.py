import RPi.GPIO as GPIO # RPi.GPIO can be referred as GPIO from now
import time
ledPin = 5
switchPin = 3
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.output(ledPin, GPIO.LOW) #turn off LED
GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(switchPin, GPIO.IN) #pin3 as input has internal pull-up
while True:
    if GPIO.input(switchPin): #read button state
        print("LED on")
        GPIO.output(ledPin, GPIO.HIGH)
        time.sleep(0.5)
        print("LED off")
        GPIO.output(ledPin, GPIO.LOW)
        time.sleep(0.5)
    else:
        GPIO.output(ledPin, GPIO.HIGH)