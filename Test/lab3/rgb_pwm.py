import time, RPi.GPIO as GPIO
INCREASING=True
DECREASING=False
RED = 16
GREEN = 20
BLUE = 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
p_red=GPIO.PWM(RED, 1000)
p_green=GPIO.PWM(GREEN, 1000)
p_blue=GPIO.PWM(BLUE, 1000)
#frequency = 1000 Hz
#define a function to control the color and brightness of the LED
def RGBColorLED(red, green, blue, increase):

    if(increase == True):
        for dc in range (0, 101, 5):
            if(red == True):
                p_red.start(dc)
            if(green == True):
                p_green.start(dc)
            if(blue == True):
                p_blue.start(dc)
            time.sleep(0.02)
    #increase in brightness
    else: #decrease in brightness
        for dc in range(100, -1, -5):
            if(red == True):
                p_red.start(dc)
            if(green == True):
                p_green.start(dc)
            if(blue == True):
                p_blue.start(dc)
            time.sleep(0.02)

#main program
try:
    while (True): #test for six combinations (exclude the cases for white and no colors)
        RGBColorLED(True, False, False, INCREASING)
        RGBColorLED(True, False, False, DECREASING)
        RGBColorLED(False, True, False, INCREASING)
        RGBColorLED(False, True, False, DECREASING)
        RGBColorLED(False, False, True, INCREASING)
        RGBColorLED(False, False, True, DECREASING)
        # yellow
        RGBColorLED(True, True, False, INCREASING)
        RGBColorLED(True, True, False, DECREASING)
        # purple
        RGBColorLED(True, False, True, INCREASING)
        RGBColorLED(True, False, True, DECREASING)
        # cyan
        RGBColorLED(False, True, True, INCREASING)
        RGBColorLED(False, True, True, DECREASING)
        # white
        RGBColorLED(True, True, True, INCREASING)
        RGBColorLED(True, True, True, DECREASING)



except KeyboardInterrupt:
    p_red.stop()
    p_green.stop()
    p_blue.stop()
    GPIO.cleanup()

