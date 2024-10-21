# sudo systemctl stop pigpiod
import RPi.GPIO as GPIO
btn_pin = 19
led_pin = 13
#interrupt handler when button pressed
def button_callback(channel):
    if GPIO.input(btn_pin):
        GPIO.output(led_pin, GPIO.LOW)
    else:
        GPIO.output(led_pin, GPIO.HIGH)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(btn_pin, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, GPIO.LOW)
#enable interrupt, both rising and falling edge triggered
GPIO.add_event_detect(btn_pin, GPIO.BOTH,callback=button_callback, bouncetime=250)
#main program
try:
    while True:
        pass
except KeyboardInterrupt:
    GPIO.cleanup()