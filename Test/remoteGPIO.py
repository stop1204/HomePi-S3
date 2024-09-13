
# 	1.	Connect the long leg of the LED to the GPIO pin of the Raspberry Pi (e.g., GPIO 17 corresponds to pin 11).
# 	2.	Connect the short leg of the LED to the ground (GND, Raspberry Pi pin 6) through a 220 ohm resistor.
"""
This Python script uses the gpiozero library to control
an LED connected to a Raspberry Pi GPIO pin via a remote host
"""
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep


factory = PiGPIOFactory(host='192.168.11.254')
led = LED(17, pin_factory=factory)
while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)