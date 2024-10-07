import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
RED = 16 #connect RED to pin22
GREEN = 20 #connect GREEN to pin18
BLUE = 21 #connect BLUE to pin16
GPIO.setwarnings(False)
GPIO.setup(RED,GPIO.OUT)
GPIO.output(RED,0)
GPIO.setup(GREEN,GPIO.OUT)
GPIO.output(GREEN,0)
GPIO.setup(BLUE,GPIO.OUT)
GPIO.output(BLUE,0)
try:
    while (True):
        request = input('Input RGB -> ')
        if (len(request) == 3):
            GPIO.output(RED,int(request[0]))
            GPIO.output(GREEN,int(request[1]))
            GPIO.output(BLUE,int(request[2]))
except KeyboardInterrupt:
    GPIO.cleanup()