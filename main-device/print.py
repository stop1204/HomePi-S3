import json
from gpiozero import LED, Button

from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont
from signal import pause
import threading
import time
import os


# GPIO.BCM
BACKLIGHT_PIN = 18  # GPIO 18，physical pin  12
BUTTON_PIN = 17     # GPIO 17，physical pin 11


backlight = LED(BACKLIGHT_PIN)
button = Button(BUTTON_PIN)

# init LCD
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, bus_speed_hz=16000000)
device = st7735(serial, width=160, height=128, rotate=1)

# init backlight
backlight.on()

# configure LCD
def update_display(msg="Button Pressed!"):
    image = Image.new("RGB", (device.width, device.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=(0, 0, 0))
    draw.text((10, 10), msg, font=font, fill=(255, 255, 255))
    device.display(image)
    print("Display updated")


# switch backlight
def toggle_backlight():
    if backlight.is_lit:
        backlight.off()
        print("Display backlight off")
    else:
        backlight.on()
        print("Display backlight on")

# button pressed event
def on_button_pressed():
    toggle_backlight()
    update_display()

# button event
button.when_pressed = on_button_pressed

print("waiting for button press...")
def check_lcd_command():
    command_file = 'lcd_command.txt'
    while True:
        if os.path.exists(command_file):
            with open(command_file, 'r') as f:
                command_data = json.load(f)
            os.remove(command_file)
            action = command_data.get('action')
            message = command_data.get('message', '')
            if action == 'display':
                update_display(message)
            elif action == 'clear':
                clear_display()
            # other actions can be added here
        time.sleep(1)

def clear_display():
    image = Image.new("RGB", (device.width, device.height))
    device.display(image)
    print("Display cleared")


threading.Thread(target=check_lcd_command, daemon=True).start()
# keep the script running
pause()