from gpiozero import LED
from time import sleep

BACKLIGHT_PIN = 18  # BCM pin , physical pin 12

backlight = LED(BACKLIGHT_PIN)

# blink BLK
for _ in range(5):
    backlight.on()
    sleep(1)
    backlight.off()
    sleep(1)