import time
import RPi.GPIO as GPIO

GPIO_TRIGGER = 29  # Pin 16 (BOARD) connected to Trigger pin of the sensor
GPIO_ECHO = 31     # Pin 18 (BOARD) connected to Echo pin of the sensor

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def measure():

    # Ensure Trigger is low
    GPIO.output(GPIO_TRIGGER, False)
    time.sleep(0.5)  # Allow sensor to settle

    # Send a 10us pulse to Trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)  # 10 microseconds
    GPIO.output(GPIO_TRIGGER, False)

    # Initialize start and stop times
    start = time.time()

    # Record the start time when Echo goes high
    while GPIO.input(GPIO_ECHO) == 0:
        start = time.time()

    # Record the stop time when Echo goes low
    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()

    # Calculate pulse duration
    elapsed = stop - start

    # Calculate distance (speed of sound = 34300 cm/s)
    distance = elapsed * 34300
    distance = distance / 2  # Round-trip distance

    return distance

# Main program
print("Ultrasonic Measurement")

while 1:
    cm = measure()
    print("Distance : %.1f cm" % cm)