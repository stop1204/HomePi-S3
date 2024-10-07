import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)
while True:
    ans = int(input("Please select tone<1-3>,press 0 to exit:"))

    if ans == 0:
        GPIO.output(35, 0)
        break
    if ans == 1:
        for r in range(1000):
            for x in range(250):
                GPIO.output(6, 1)
            for x in range(250):
                GPIO.output(6, 0)
    #duration for high
    #duration for low
    if ans == 2:
        for r in range(1000):
            for x in range(100):
                GPIO.output(6, 1)
            for x in range(100):
                GPIO.output(6, 0)



    if ans == 3:
        for r in range(1000):
            pass
            for x in range(500):
                GPIO.output(6, 1)
            for x in range(500):
                GPIO.output(6, 0)