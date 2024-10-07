import time, RPi.GPIO as GPIO
GPIO.setwarnings(False) #ignore all warnings
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT) #pin3 as output
GPIO.setup(10, GPIO.OUT) #pin5 as output
p1 = GPIO.PWM(8, 1000) #set pin3 in PWM frequency to 1000Hz
p2 = GPIO.PWM(10, 10) #set pin5 in PWM to 10 Hz
while True:
    for dc in range (5, 101, 5):
        p1.start(dc)
        p2.start(dc)
        time.sleep(0.2)