
# 	1.	Connect the long leg of the LED to the GPIO pin of the Raspberry Pi (e.g., GPIO 17 corresponds to pin 11).
# 	2.	Connect the short leg of the LED to the ground (GND, Raspberry Pi pin 6) through a 220 ohm resistor.
"""
This Python script uses the gpiozero library to control
an LED connected to a Raspberry Pi GPIO pin via a remote host
"""
from gpiozero import LED,PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep


factory = PiGPIOFactory(host='192.168.8.104')
led = LED(17, pin_factory=factory)
# test the PWMLED
pwm_led = PWMLED(18, pin_factory=factory)
while True:
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)

    for i in range(0, 100):
        pwm_led.value = i / 100
        sleep(0.01)
    for i in range(100, 0, -1):
        pwm_led.value = i / 100
        sleep(0.01)
