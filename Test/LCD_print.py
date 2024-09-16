from gpiozero import LED, Button

from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont
from signal import pause




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
def update_display():
    image = Image.new("RGB", (device.width, device.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=(0, 0, 0))
    draw.text((10, 10), "Button Pressed!", font=font, fill=(255, 255, 255))
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

# keep the script running
pause()