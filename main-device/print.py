import io
import json
from gpiozero import LED, Button

from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from PIL import Image, ImageDraw, ImageFont
from signal import pause
import threading
import time
import os
import requests
import cairosvg
import re
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
# pip install sympy --break-system-packages
# pip install cairosvg --break-system-packages

# GPIO.BCM
BACKLIGHT_PIN = 18  # GPIO 18，physical pin  12
BUTTON_PIN = 17     # GPIO 17，physical pin 11


backlight = LED(BACKLIGHT_PIN)
button = Button(BUTTON_PIN)

# init LCD
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, bus_speed_hz=36000000)
device = st7735(serial, width=160, height=128, rotate=1)

# init backlight
backlight.on()

qr_code_visible = False

# configure LCD
def update_display(msg="",xy=(10,10),fill=(255,255,255)):
    image = Image.new("RGB", (device.width, device.height))
    if msg:
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.rectangle((0, 0, device.width, device.height), outline=0, fill=(0, 0, 0))
        draw.text(xy=xy, text=msg, font=font, fill=fill)
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
def qr_code_btn():
    global qr_code_visible
    if qr_code_visible == False:
        qr_code_visible = True
        tunnel_url = get_tunnel_url()
        if tunnel_url:
            print(f"Tunnel URL: {tunnel_url}")
            svg_data = get_qr_code(tunnel_url)
            if svg_data:
                display_qr_code_on_lcd(svg_data)
    else:
        qr_code_visible = False
        clear_display()

# button pressed event
def on_button_pressed():
    # toggle_backlight()
    qr_code_btn()


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
            # if action == 'display':
            #     update_display(message)
            # elif action == 'clear':
            #     clear_display()

            match action:
                case 'display':
                    update_display(message)
                case 'clear':
                    clear_display()
                case 'show qr code':
                    qr_code_btn()
                case _: pass

            # other actions can be added here
        time.sleep(1)

def clear_display():
    image = Image.new("RGB", (device.width, device.height))
    device.display(image)
    print("Display cleared")

# /home/terry/HomePi-S3/
def get_tunnel_url(file_path="../nohup.out"):
    with open(file_path, 'r') as file:
        content = file.read()
        match = re.search(r'Tunnel established at (http[^\s]+)', content)
        if match:
            return match.group(1)
        else:
            print("No tunnel URL found.")
            return None
def get_qr_code(url_text):
    api_url = f"https://public-api.qr-code-generator.com/v1/create/free?image_format=SVG&image_width=500&foreground_color=%23000000&frame_color=%23000000&frame_name=no-frame&qr_code_text={url_text}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to fetch QR code.")
        return None
def display_qr_code_on_lcd(svg_data):
    # svg to png
    png_data = cairosvg.svg2png(bytestring=svg_data)

    # png to pillow
    image = Image.open(io.BytesIO(png_data))

    # resige image
    image = image.resize((device.width, device.height))


    device.display(image)
    print("QR code displayed on LCD.")


threading.Thread(target=check_lcd_command, daemon=True).start()
# keep the script running
pause()