import time
import RPi.GPIO as GPIO

GPIO_TRIGGER = 29
GPIO_ECHO = 31

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def measure():



    # Send a 10us pulse to Trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)  # 10 microseconds
    GPIO.output(GPIO_TRIGGER, False)

    start = time.time()

    # Record the start time when Echo goes high
    while GPIO.input(GPIO_ECHO) == 0:
        start = time.time()

    # Record the stop time when Echo goes low
    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()

    elapsed = stop - start

    distance = (elapsed * 34300) / 2  # Round-trip distance

    return distance

def measure_average():

    distances = []
    for _ in range(3):
        dist = measure()
        distances.append(dist)
        time.sleep(0.1)  # 0.1 second interval between measurements
    average_distance = sum(distances) / len(distances)
    return average_distance

# Main program
print("Ultrasonic Measurement")

try:
    while True:
        cm = measure_average()
        print("Distance : %.1f cm" % cm)
        time.sleep(1)  # Wait for 1 second before next measurement
except KeyboardInterrupt:
    GPIO.cleanup()