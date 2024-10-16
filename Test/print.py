import io
import json
import string


from gpiozero import LED, Button  # 1/10/2024 will be removed

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
from enum import Enum

# pip install sympy --break-system-packages
# pip install cairosvg --break-system-packages
# brew install python3-rpi-gpio
# GPIO.BCM


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

BACKLIGHT_PIN = 18  # GPIO 18，physical pin  12  # changed to show the QR code
BUTTON_PIN = 17     # GPIO 17，physical pin 11
TOUCH_PIN = 20      # touch by hand, for test function
LED_PIN = 21        # trigger by touch, for test function
SIZE_DETECT_PIN = 16 # print the size of LCD


GPIO.setup(SIZE_DETECT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(TOUCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# init LCD
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, bus_speed_hz=36000000)
device = st7735(serial, width=160, height=128, rotate=1)
time.sleep(0.2)
backlight = LED(BACKLIGHT_PIN)
backlight.on()
# init backlight

time.sleep(0.2)

display_buffer = []
BUFFER_LIMIT = 100
char_width, char_height=0,0


def calculate_screen_size():
    global char_width, char_height
    image = Image.new("RGB", (device.width, device.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Get the size of one character to calculate maximum rows and columns
    char_width, char_height = draw.textsize("A", font=font)

    # Calculate the maximum number of rows and columns
    max_cols = device.width // char_width
    max_rows = device.height // char_height

    # Define gradient colors (starting from blue to red)
    start_color = (0, 0, 255)  # Blue
    end_color = (255, 0, 0)    # Red

    def interpolate_color(start_color, end_color, factor):
        """Interpolates between two colors by a factor (0 to 1)."""
        return tuple(int(start + factor * (end - start)) for start, end in zip(start_color, end_color))

    # Draw the letters in a row (A-Z) with a horizontal gradient
    row_letters = string.ascii_uppercase[:max_cols]
    for i, letter in enumerate(row_letters):
        factor = i / max_cols  # Calculate factor for gradient
        color = interpolate_color(start_color, end_color, factor)
        draw.text((0 + i * char_width, 0), letter, font=font, fill=color)

    # Draw the letters in a column (A-Z) with a vertical gradient
    for i in range(min(max_rows, len(string.ascii_uppercase))):
        factor = i / max_rows  # Calculate factor for gradient
        color = interpolate_color(start_color, end_color, factor)
        draw.text((0,  i * char_height), string.ascii_uppercase[i], font=font, fill=color)

    draw.text((0,(max_rows-2)*char_height), f"Max rows: {max_rows}", font=font, fill=ColorPalette.RED.value)
    draw.text((0,(max_rows-1)*char_height), f"Max columns: {max_cols}", font=font, fill=ColorPalette.RED.value)
    # Display the image on the screen
    device.display(image)

    print(f"Max rows: {max_rows}, Max columns: {max_cols}")

    # draw.text((10, 10 + max_rows * char_height), f"Max rows: {max_rows}, Max columns: {max_cols}", font=font, fill=(255, 255, 255))


# Enum for predefined colors
# ColorPalette.RED.value  (255, 0, 0)
class ColorPalette(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    ORANGE = (255, 165, 0)
    INDIGO = (75, 0, 130)
    PINK = (255, 192, 203)

def clear_display():
    image = Image.new("RGB", (device.width, device.height))
    device.display(image)
    print("Display cleared")


# configure LCD
def update_display(msg="",xy=(10,10),fill=(255,255,255)):

    image = Image.new("RGB", (device.width, device.height))

    print("have text")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=(0, 0, 0))
    draw.text(xy=xy, text=msg, font=font, fill=fill)
    device.display(image)
    print("Display updated")

# for test
def update_display2(msg="Button Pressed!"):
    image = Image.new("RGB", (device.width, device.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=(0, 0, 0))
    draw.text((10, 10), msg, font=font, fill=(255, 255, 255))
    device.display(image)
    print("Display updated")
# switch backlight
def toggle_backlight():

    if GPIO.input(BACKLIGHT_PIN) == GPIO.HIGH:
        GPIO.output(BACKLIGHT_PIN, GPIO.LOW)
        print("Display backlight off")

    else:
        GPIO.output(BACKLIGHT_PIN, GPIO.HIGH)
        update_display2()
        print("Display backlight on")

def qr_code_btn():

    clear_display()

    tunnel_url = get_tunnel_url()
    if tunnel_url:
        print(f"Tunnel URL: {tunnel_url}")
        svg_data = get_qr_code(tunnel_url)
        if svg_data:
            display_qr_code_on_lcd(svg_data)



# button pressed event
def on_button_pressed():

    qr_code_btn()


def check_lcd_command():
    command_file = '../lcd_command.txt'
    while True:
        if os.path.exists(command_file):
            print("loaded command")
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
                    update_display(msg=message)
                case 'clear':
                    clear_display()

                case 'show qr code':
                    qr_code_btn()
                case _: pass

            # other actions can be added here
        time.sleep(1)




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





def event():
    try:
        while True:
            # pressed
            if GPIO.input(TOUCH_PIN) == GPIO.LOW:
                toggle_backlight()
                print("touched")

            if GPIO.input(SIZE_DETECT_PIN) == GPIO.LOW:
                calculate_screen_size()
                print("size detect")
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                on_button_pressed()
                print("button pressed")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("monitoring stopped")




# update_display2()

print("waiting for button press...")
threading.Thread(target=check_lcd_command, daemon=True).start()
threading.Thread(target=event, daemon=True).start()
# keep the script running
pause()


