import io
import json
import string
import subprocess
import sys

from PIL.ImageStat import Global
from anyio import sleep
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
from enum import Enum
from queue import Queue
import logging
import datetime
import RPi.GPIO as GPIO
import textwrap

# from DHT11 import DHT11  # call the customer  library
import board
import adafruit_dht

import base64
import openai
import sounddevice as sd
import wavio


# turn to normal permission, because the AI function does not need the root permission
#rc.lcoal: su - terry -c "python3 /home/terry/Desktop/HomePi-S3/main-device/print.py &"

GPIO.cleanup()



# 接著是主程序邏輯
# 例如：
print("Running as user:", os.getuid())
GPIO.setmode(GPIO.BCM)
# GPIO Configuration using gpiozero
BACKLIGHT_PIN = 18      # Backlight controlled via GPIO 18
BUTTON_UP_PIN = 23      # Yellow-Up (GPIO 20) -> change to 23
BUTTON_LEFT_PIN = 17    # Red-Left (GPIO 17)
BUTTON_RIGHT_PIN = 22   # Green-Right (GPIO 16) -> change to 22
BUTTON_DOWN_PIN = 27    # Blue-Bottom (GPIO 21) -> change to 27
time.sleep(0.2)
# DHT11_PIN = DHT11(pin=26)      # GPIO 26，physical pin 37
dht_device = adafruit_dht.DHT11(board.D26,use_pulseio=False) # init sensor, use GPIO 26

# Initialize Backlight LED
backlight = LED(BACKLIGHT_PIN)
# backlight.on() will be called before initialize_menu()

# initialize the Door and LED of door
DOOR_LED_PIN = 16
OPEN_DOOR_PIN = 21
CLOSE_DOOR_PIN = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_LED_PIN, GPIO.OUT)
GPIO.setup(OPEN_DOOR_PIN, GPIO.OUT)
GPIO.setup(CLOSE_DOOR_PIN, GPIO.OUT)

# Initialize Buttons
button_up = Button(BUTTON_UP_PIN)        # Yellow-Up
button_left = Button(BUTTON_LEFT_PIN)    # Red-Left
button_right = Button(BUTTON_RIGHT_PIN)  # Green-Right
button_down = Button(BUTTON_DOWN_PIN)    # Blue-Bottom

# Initialize HC-SR04
GPIO_TRIGGER = 5  # BOARD 29
GPIO_ECHO = 6     # BOARD 31
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
automatic_door_mode = 3 # guard mode 2, automatic mode 3, silent mode 4
BUZZER_PIN = 12
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize FAN
FAN_PIN = 14
GPIO.setup(FAN_PIN, GPIO.OUT)

# Initialize LCD
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, bus_speed_hz=36000000)
device = st7735(serial, width=160, height=128, rotate=1)

time.sleep(0.2)

# Initialize Character Dimensions
char_width, char_height = 0, 0



# setup logging
rootpath = "/home/terry/Desktop/HomePi-S3/"

LOG_FILE = "operation.log"
IP = "0.0.0.0"
BT = {}
DHT = {}

# Define Password Dictionary,  1: Yellow-Up, 2: Red-Left, 3: Green-Right, 4: Blue-Bottom
password_dict = {
    "restart": [2, 2, 2, 2, 2]  # Press the buttons in this order to restart the script
    ,
    # "shutdown": [4, 3, 2, 1]
}
button_sequence = []  # Stores the sequence of button presses

# Clear the log file on startup
with open(LOG_FILE, 'w') as log_file:
    log_file.write("Operation Log Initialized at {}\n".format(datetime.datetime.now().strftime("%H:%M")))

# Configure logging to append with timestamps
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M'
)

current_mode = "menu"  # menu or action or scrolling or keyboard
scroll_context = None

selected_wifi_network = None

# Initialize Command Queue
command_queue = Queue()
command_files = [rootpath+'/lcd_command.txt', rootpath+'../lcd_command.txt']


#========================this is for AI part========================

# Configure OpenAI API key
LEPTON_API_TOKEN="xhwg2y4dpim3vqu16z8ijtjxk12e93u6"
# LEPTON_API_TOKEN = os.getenv("LEPTON_API_TOKEN")
if not LEPTON_API_TOKEN:
    raise ValueError("Environment variable LEPTON_API_TOKEN must be set")

client = openai.OpenAI(
    base_url="https://qwen2-72b.lepton.run/api/v1/",
    api_key=LEPTON_API_TOKEN
)
# Audio recording settings
SAMPLE_RATE = 16000  # Hertz
CHANNELS = 1
RECORD_DURATION = 5  # Seconds
AUDIO_FORMAT = "opus"
BITRATE = 16
# GPIO setup
AI_BUTTON_PIN = 19  # GPIO pin number for the button
AI_LED_PIN = 13     # GPIO pin number for the LED
GPIO.setup(AI_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set button as input with pull-up resistor
GPIO.setup(AI_LED_PIN, GPIO.OUT)  # Set LED as output
role_system = {
    "role": "system",
    "content": (
        "You are a smart home assistant. Please convert the user's natural language command from the following audio into a JSON object with 'action' and 'message' fields based on the predefined actions below. Return only the JSON object.\n"
        "Predefined actions:\n"
        # "- action: 'display', message: <display message>\n"
        # "- action: 'clear', message: ''\n"
        # "- action: 'qr_code', message: ''\n"
        # "- action: 'unknown', message: ''\n"
        "- action: '[OPEN_DOOR]', message: ''\n"
        "- action: '[CLOSE_DOOR]', message: ''\n"
        "- action: '[TURN_ON_LIGHT]', message: ''\n"
        "- action: '[TURN_OFF_LIGHT]', message: ''\n"
        "- action: '[TURN_ON_FAN]', message: ''\n"
        "- action: '[TURN_OFF_FAN]', message: ''\n"
        "- action: '[GUARD_MODE]', message: ''\n"
        "- action: '[AUTOMATIC_MODE]', message: ''\n"
        "- action: '[Silent_Mode]', message: ''\n"
        "- action: '[UNKNOWN_COMMAND]', message: ''\n"
        "AUTOMATIC_MODE and Silent_Mode and GUARD_MODE is distance detect mode.\n"
        "Ensure the response is a valid JSON object. If the command does not match any of the above, set 'action' to 'unknown' and 'message' to an empty string."
    )
}
#==================================END================================



class ScrollContext:
    def __init__(self, content_lines, reverse_order=False):
        if reverse_order:
            content_lines = list(reversed(content_lines))
        self.content_lines = content_lines
        self.total_lines = len(content_lines)
        self.current_scroll_index = 0
        self.lines_per_page = (device.height // char_height) - 2  # KEEP 2 lines for the operation instructions

    def scroll_up(self):
        if self.current_scroll_index > 0:
            self.current_scroll_index -= 1
            logging.info(f"Scrolled up to line {self.current_scroll_index}")
            print(f"Scrolled up to line {self.current_scroll_index}")

    def scroll_down(self):
        if self.current_scroll_index < self.total_lines - self.lines_per_page:
            self.current_scroll_index += 1
            logging.info(f"Scrolled down to line {self.current_scroll_index}")
            print(f"Scrolled down to line {self.current_scroll_index}")

    def get_visible_lines(self):
        return self.content_lines[self.current_scroll_index:self.current_scroll_index + self.lines_per_page]

# Define Color Palette
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
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

# Define MenuItem and Menu Classes
class MenuItem:
    def __init__(self, title, action=None, children=None):
        self.title = title
        self.action = action  # Function or command
        self.children = children if children else []

class Menu:
    def __init__(self, root):
        self.root = root
        self.current = root
        self.history = []
        self.selected_index = 0

    def navigate_up(self):
        if self.selected_index > 0:
            self.selected_index -= 1
            render_menu()

    def navigate_down(self):
        if self.selected_index < len(self.current.children) - 1:
            self.selected_index += 1
            render_menu()

    def select(self):
        selected_item = self.current.children[self.selected_index]
        if selected_item.children:
            self.history.append((self.current, self.selected_index))
            self.current = selected_item
            self.selected_index = 0
            render_menu()
        elif selected_item.action:
            selected_item.action()
            # set_mode_action()

    def back(self):
        global current_mode
        if current_mode == "action":
            # Return to menu from action
            set_mode_menu() # current_mode = "menu"
            render_menu()
        else:
            if self.history:
                self.current, self.selected_index = self.history.pop()
                render_menu()

    def get_display_items(self):
        return [item.title for item in self.current.children]



class IoTHttp:
    """
    update:https://sgp1.blynk.cloud/external/api/update?token=34RJEE0vA7lH4A2E2lmFpUD63vcu63J_&v0=value
    get:https://sgp1.blynk.cloud/external/api/get?token=34RJEE0vA7lH4A2E2lmFpUD63vcu63J_&v0
    # set:https://sgp1.blynk.cloud/external/api/update/property?token=34RJEE0vA7lH4A2E2lmFpUD63vcu63J_&pin=v0&color=%2374747a

    """
    """
    add enum to map the pin
    v0: LED   on 1 / off 0
        https://sgp1.blynk.cloud/external/api/update?token=34RJEE0vA7lH4A2E2lmFpUD63vcu63J_&v0=0
    v1: DOOR   on 1 / off 0
    V2: CURTAIN  on 1 / off 0
    V3: HUMIDITY 
    V4: TEMP
    """


    def __init__(self):
        self.url = "https://sgp1.blynk.cloud/external/api/"
        self.token = "34RJEE0vA7lH4A2E2lmFpUD63vcu63J_"
        self.tag = {
            "LED": 0,
            "DOOR": 1,
            "CURTAIN": 2,
            "HUMIDITY": 3,
            "TEMP": 4}

    def get(self, pin):
        response = requests.get(f"{self.url}get?token={self.token}&v{pin}")

        # return response.json()

    def update(self,pin, data):
        response = requests.get(f"{self.url}update?token={self.token}&v{pin}={data}")
        # return response.json()

def wrap_text(text, max_width):
    return textwrap.wrap(text, width=max_width)

# Define Menu Actions
def display_device_status():
    global IP,BT,scroll_context
    status = (f"Device Status:\n- Backlight: On\n- Buttons: Active\n- LCD: Working"
              f"\n- IP:{IP}"
              f"\n- Bluetooth:"
              f"\n  - Name: {BT.get('Name', 'Unknown')}"
              f"\n  - Powered: {BT.get('Powered', 'Unknown')}"
              f"\n  - Discoverable: {BT.get('Discoverable', 'Unknown')}")
    # update_display(msg=status)
    logging.info("device status.")
    set_mode_scrolling()
    lines = status.split('\n')
    scroll_context = ScrollContext(content_lines=lines)
    render_scrolling_display()
    # render_menu()  # Display "<- Back"

def clear_screen():
    clear_display()
    logging.info("Cleared the display.")
    set_mode_action()
    # render_menu()  # Display "<- Back"

def show_qr_code():
    qr_code_btn()
    logging.info("QR code.")
    set_mode_action()
    # render_menu()  # Display "<- Back"

# def display_custom_message():
#     update_display("Custom Message!")
#     logging.info("Displayed custom message.")
# Define Menu Actions
def display_custom_message():
    global scroll_context
    message = ("Hello, World!\n"
               "This is a custom message displayed on the LCD.\n"
               "You can scroll up and down to read all the content.\n"
               "Enjoy using your Raspberry Pi!\n")
    # update_display(msg=message)
    logging.info(f"message: '{message}'")
    set_mode_scrolling()
    lines = message.split('\n')
    # scroll_context = ScrollContext(content_lines=lines)
    wrapped_lines = []
    for line in lines:
        wrapped_lines.extend(wrap_text(line, device.width // char_width))
    scroll_context = ScrollContext(content_lines=wrapped_lines)
    render_scrolling_display()
    # render_menu()  # Display "<- Back"

def display_console_logs():
    global scroll_context
    set_mode_scrolling()
    if not os.path.exists(LOG_FILE):
        update_display("No logs available.")
        logging.warning("Attempted to display logs, but log file does not exist.")
    else:
        with open(LOG_FILE, 'r') as log_file:
            logs = log_file.read()
        # update_display(msg=logs)
        logging.info("console logs.")
        lines = logs.split('\n')
        lines = list(reversed(lines))
        # scroll_context = ScrollContext(content_lines=lines)
        wrapped_lines = []
        for line in lines:
            wrapped_lines.extend(wrap_text(line, device.width // char_width))
        scroll_context = ScrollContext(content_lines=wrapped_lines)
        render_scrolling_display()
    # render_menu()  # Display "<- Back"


# Create Menu Structure
root_menu = MenuItem("Main Menu", children=[
    MenuItem("Display Message", action=lambda: display_custom_message()),
    MenuItem("Show Web Addr.", action=show_qr_code),
    MenuItem("Device Status", action=display_device_status),
    MenuItem("WIFI", action=lambda: display_wifi_status()),
    # MenuItem("WIFI",action=lambda: display_wifi_status(), children=[
    #     MenuItem(selected_wifi_network, action=lambda: scan_wifi_networks())  # level 2 menu item
    #     MenuItem("Scan WIFI", action=lambda: scan_wifi_networks())  # level 2 menu item
    # ]),
    MenuItem("Clear Screen", action=clear_screen),
    MenuItem("Console", action=display_console_logs)  # New Console menu item
])

menu = Menu(root_menu)

# Function to Calculate Screen Size and Character Dimensions
def calculate_screen_size():
    global char_width, char_height
    image = Image.new("RGB", (device.width, device.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # Get size of one character using textbbox
    bbox = draw.textbbox((0, 0), "A", font=font)
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]

    # Calculate max rows and columns
    max_cols = device.width // char_width
    max_rows = device.height // char_height

    print(f"Max rows: {max_rows}, Max columns: {max_cols}")

# Function to Clear Display
def clear_display():
    image = Image.new("RGB", (device.width, device.height), ColorPalette.BLACK.value)
    device.display(image)
    print("Display cleared")

# Function to Update Display with a Message
def update_display(msg="", xy=(10,10), fill=ColorPalette.WHITE.value):
    image = Image.new("RGB", (device.width, device.height), ColorPalette.BLACK.value)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.multiline_text(xy=xy, text=msg, font=font, fill=fill)
    device.display(image)
    print("Display updated")

# Function to Toggle Backlight
def toggle_backlight():
    global current_mode
    if backlight.is_lit:
        backlight.off()
        print("Display backlight off")
    else:
        backlight.on()
        update_display(msg="Backlight On")
        print("Display backlight on")

# Function to Set Mode to Action
def set_mode_action():
    global current_mode
    current_mode = "action"
    print(f"mode: {current_mode}")
# Function to Set Mode to scrolling
def set_mode_scrolling():
    global current_mode
    current_mode = "scrolling"
    print(f"mode: {current_mode}")
# function to set mode to keyboard
def set_mode_keyboard():
    global current_mode
    current_mode = "keyboard"
    print(f"mode: {current_mode}")
def set_mode_menu():
    global current_mode
    current_mode = "menu"
    print(f"mode: {current_mode}")
def display_wifi_status():
    global scroll_context,current_wifi_network
    try:
        # get active wifi connection
        result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        connected_ssid = "N/A"
        for line in lines:
            active, ssid = line.split(':')
            if active == 'yes':
                connected_ssid = ssid
                break
        status = f"Connected WIFI: {connected_ssid}\n\nPress Right-btn to\n scan WiFi"
    except Exception as e:
        status = "Connected WIFI: N/A\n\nPress Right-btn to\n scan WiFi"
        logging.error(f"Error fetching WiFi status: {e}")
    lines = wrap_text(status, device.width // char_width)
    scroll_context = ScrollContext(content_lines=lines)
    render_scrolling_display()
    logging.info("WIFI status.")
def scan_wifi_networks():
    global scroll_context, selected_wifi_network
    try:
        # get active wifi connection
        result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY', 'dev', 'wifi', 'list'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        wifi_networks = []
        for line in lines:
            ssid, security = line.split(':')
            wifi_networks.append(f"{ssid} ({security})")
        if not wifi_networks:
            wifi_networks = ["No WIFI networks found."]
    except Exception as e:
        wifi_networks = ["Error scanning WIFI networks."]
        logging.error(f"Error scanning WiFi networks: {e}")
    wrapped_lines = []
    for network in wifi_networks:
        wrapped_lines.extend(wrap_text(network, device.width // char_width))

    scroll_context = ScrollContext(content_lines=wrapped_lines)
    selected_wifi_network = None
    render_scrolling_display()
    logging.info("scanned WIFI networks.")
# Function to Generate and Display QR Code
def qr_code_btn():
    clear_display()
    tunnel_url = get_tunnel_url()
    if tunnel_url:
        print(f"Tunnel URL: {tunnel_url}")
        svg_data = get_qr_code(tunnel_url)
        if svg_data:
            display_qr_code_on_lcd(svg_data)

# Function to Get Tunnel URL from File
def get_tunnel_url(file_path="/nohup.out"):
    global rootpath
    path = rootpath + file_path
    if not os.path.exists(path):
        print("Tunnel URL file not found.")
        return None
    with open(path, 'r') as file:
        content = file.read()
        match = re.search(r'Tunnel established at (http[^\s]+)', content)
        if match:
            return match.group(1)
        else:
            print("No tunnel URL found.")
            return None

# Function to Fetch QR Code from API
def get_qr_code(url_text):
    api_url = f"https://public-api.qr-code-generator.com/v1/create/free?image_format=SVG&image_width=500&foreground_color=%23000000&frame_color=%23000000&frame_name=no-frame&qr_code_text={url_text}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to fetch QR code.")
        return None

# Function to Display QR Code on LCD
def display_qr_code_on_lcd(svg_data):
    # Convert SVG to PNG
    png_data = cairosvg.svg2png(bytestring=svg_data)
    # Open PNG with Pillow
    image = Image.open(io.BytesIO(png_data))
    # Resize Image to Fit LCD
    image = image.resize((device.width, device.height))
    device.display(image)
    print("QR code displayed on LCD.")

# Function to Render the Menu on LCD
def render_menu():
    global current_mode
    set_mode_menu()
    image = Image.new("RGB", (device.width, device.height), ColorPalette.BLACK.value)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # if current_mode == "menu":
    menu_items = menu.get_display_items()
    for idx, item in enumerate(menu_items):
        if idx == menu.selected_index:
            # fill = ColorPalette.YELLOW.value  # Highlighted item color
            background_color = ColorPalette.BLUE.value
            text_color = ColorPalette.WHITE.value
        else:
            # fill = ColorPalette.WHITE.value
            # fill = ColorPalette.YELLOW.value  # Highlighted item color
            background_color = ColorPalette.BLACK.value
            text_color = ColorPalette.WHITE.value

        y_position = idx * char_height
        # Ensure text is within display bounds
        if y_position + char_height < device.height - char_height:
            # draw.text((10, y_position), item, font=font, fill=fill)
            # background
            draw.rectangle(
                [(0, y_position), (device.width, y_position + char_height)],
                fill=background_color
            )
            # text
            draw.text((10, y_position), item, font=font, fill=text_color)

    # Display operation instructions on the last line
    if menu.history:
        instruction = "<- Back"
    else:
        instruction = "Select -> "
        if DHT.get('temperature') is not None:
            instruction += f"{DHT['temperature']}°C,H:{DHT['humidity']}%"
        else:

            # instruction += "N/A,Err:{}".format(DHT.get('error_code', '-1'))
            instruction += "Sys:{}".format(DHT.get('sys_temp', '-1'))
    draw.text((0, device.height - char_height), instruction, font=font, fill=ColorPalette.CYAN.value)
    # elif current_mode == "action":
    #     # In action mode, just display the action content and "<- Back"
    #     # Assuming the action has already updated the display
    #     draw.text((0, device.height - char_height), "<- Back", font=font, fill=ColorPalette.CYAN.value)

    device.display(image)

def render_scrolling_display():
    global scroll_context, current_mode
    if not scroll_context:
        return  #  No content to display


    set_mode_scrolling() # current_mode = "scrolling"  # set current mode to scrolling

    image = Image.new("RGB", (device.width, device.height), ColorPalette.BLACK.value)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    # status text
    status_text = f"{scroll_context.total_lines} L, V: {scroll_context.current_scroll_index + 1}-{min(scroll_context.current_scroll_index + scroll_context.lines_per_page, scroll_context.total_lines)}"
    draw.text((0, 0), status_text, font=font, fill=ColorPalette.CYAN.value)

    # Display visible lines
    visible_lines = scroll_context.get_visible_lines()
    for idx, line in enumerate(visible_lines):
        y_position = (idx + 1) * char_height  # skip the status line
        draw.text((10, y_position), line, font=font, fill=ColorPalette.WHITE.value)

    # show scrolling instructions
    instruction = "<- Back"
    draw.text((0, device.height - char_height), instruction, font=font, fill=ColorPalette.CYAN.value)

    device.display(image)
    logging.info("Scrolling display rendered.")
# Function to Handle Menu Actions
def handle_menu_action(action):
    if callable(action):
        action()
        set_mode_action()
        render_menu()  # Ensure the back instruction is displayed

def button_press_handler(button):
    """
    Handle button press events
    :param button: "up", "down", "right", "left"
    mapping values: 1: Yellow-Up, 2: Red-Left, 3: Green-Right, 4: Blue-Bottom
    :return: nil
    """
    value = 0
    if button == "up":
        value = 1
    elif button == "down":
        value = 4
    elif button == "right":
        value = 3
    elif button == "left":
        value = 2

    global button_sequence
    if len(button_sequence)<5:
        button_sequence.append(value)
    else:
        button_sequence.pop(0)
        button_sequence.append(value)

    for key, value in password_dict.items():
        if button_sequence == value:
            button_sequence.pop(0)
            button_sequence.append(0)
            print(f"Password matched: {key}")
            if key == "restart":
                logging.info("Restarting script.")
                update_display("Restarting script...")
                # os.system("sudo reboot")
                # release gpio
                GPIO.cleanup()

                subprocess.run(['sudo',rootpath+'main-device/print.sh','&'])
                # sys.exit("Restarting script...")
                # os._exit(0)
                exit(0)

            elif key == "shutdown":
                logging.info("Shutting down device.")
                update_display("Shutting down device...")
                time.sleep(1)
                os.system("sudo shutdown now")

            break

# Button Press Handlers
def button_up_pressed():
    global current_mode, scroll_context
    button_press_handler("up")
    if current_mode == "menu":
        print("Yellow-Up pressed")
        menu.navigate_up()
    elif current_mode == "scrolling":
        print("Yellow-Up pressed, scrolling up")
        if scroll_context:
            scroll_context.scroll_up()
            render_scrolling_display()
        else:
            logging.error("Scroll context is None while in scrolling mode.")
def button_down_pressed():
    global current_mode, scroll_context
    button_press_handler("down")
    if current_mode == "menu":
        print("Blue-Bottom pressed")
        menu.navigate_down()

    elif current_mode == "scrolling":
        print("Blue-Bottom pressed, scrolling down")

        if scroll_context:
            scroll_context.scroll_down()
            render_scrolling_display()
        else:
            logging.error("Scroll context is None while in scrolling mode.")
def button_select_pressed():
    global current_mode, scroll_context
    button_press_handler("right")
    if current_mode == "menu":
        # print("Green-Right pressed")
        menu.select()

def button_back_pressed():
    global current_mode, scroll_context
    button_press_handler("left")
    # print("Red-Left pressed")
    if current_mode == "scrolling":
        set_mode_menu()
        scroll_context = None
        render_menu()
        logging.info("Returned to menu from scrolling mode.")
    else:
        menu.back()



# Bind Button Events to Handlers
button_up.when_pressed = button_up_pressed
button_down.when_pressed = button_down_pressed
button_right.when_pressed = button_select_pressed
button_left.when_pressed = button_back_pressed

# Function to Check and Queue External Commands
def check_lcd_command():
    global rootpath,command_files

    while True:
        for command_file in command_files:
            if os.path.exists(command_file):
                print(f"Loaded command from {command_file}")
                with open(command_file, 'r') as f:
                    try:
                        command_data = json.load(f)
                    except json.JSONDecodeError:
                        print("Invalid JSON in command file.")
                        command_data = {}
                os.remove(command_file)
                action = command_data.get('action')
                message = command_data.get('message', '')
                """
                        "- action: '[OPEN_DOOR]', message: ''\n"
                        "- action: '[CLOSE_DOOR]', message: ''\n"
                        "- action: '[TURN_ON_LIGHT]', message: ''\n"
                        "- action: '[TURN_OFF_LIGHT]', message: ''\n"
                        "- action: '[TURN_ON_FAN]', message: ''\n"
                        "- action: '[TURN_OFF_FAN]', message: ''\n"
                        "- action: '[UNKNOWN_COMMAND]', message: ''\n"
                """
                if action == 'display':
                    logging.info(f"External command: display '{message}'")
                    command_queue.put(('display', message))
                elif action == 'clear':
                    logging.info("External command: clear")
                    command_queue.put(('clear', ''))
                elif action == 'show qr code':
                    logging.info("External command: show qr code")
                    command_queue.put(('qr_code', ''))
                elif action == '[OPEN_DOOR]':
                    logging.info("External command: open door")
                    command_queue.put(('door', 'open'))
                elif action == '[CLOSE_DOOR]':
                    logging.info("External command: close door")
                    command_queue.put(('door', 'close'))
                elif action == '[TURN_ON_LIGHT]':
                    logging.info("External command: turn on light")
                    command_queue.put(('light', 'on'))
                elif action == '[TURN_OFF_LIGHT]':
                    logging.info("External command: turn off light")
                    command_queue.put(('light', 'off'))
                elif action == '[TURN_ON_FAN]':
                    logging.info("External command: turn on fan")
                    command_queue.put(('fan', 'on'))
                elif action == '[TURN_OFF_FAN]':
                    logging.info("External command: turn off fan")
                    command_queue.put(('fan', 'off'))
                elif action == '[GUARD_MODE]':
                    logging.info("External command: guard mode")
                    command_queue.put(('guard_mode', ''))
                elif action == '[AUTOMATIC_MODE]':
                    logging.info("External command: automatic mode")
                    command_queue.put(('automatic_mode', ''))
                elif action == '[Silent_Mode]':
                    logging.info("External command: silent mode")
                    command_queue.put(('silent_mode', ''))
                elif action == '[UNKNOWN_COMMAND]':
                    pass
        time.sleep(1)
# https://blynk.cloud/dashboard/450351/global/devices/1/organization/450351/devices/2663885/dashboard
def dht11_read():
    global DHT,current_mode,dht_device,rootpath,command_files


    try:
        while True:
            try:
                # result = DHT11_PIN.read()
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                if humidity is not None and temperature is not None:
                    DHT['temperature'] = temperature
                    DHT['humidity'] = humidity

                    # remove the 'C and %'
                    DHT['temperature'] = temperature
                    DHT['humidity'] = humidity
                    IoTHttp().update(IoTHttp().tag['TEMP'], temperature)
                    IoTHttp().update(IoTHttp().tag['HUMIDITY'], humidity)
                    print(f"Temp.: {temperature:.1f}C, H: {humidity:.1f}%")
                    # if temperature > 28: open the fan
                    if temperature > 28:
                        # for command_file in command_files:
                        #     if os.path.exists(command_file):
                        #         with open(command_file, 'w') as f:
                        #             f.write(json.dumps({'action': 'action', 'message': '[TURN_ON_FAN]'}))
                        fan_action('on')
                        logging.info("Fan turned on.")
                    elif temperature < 23:
                        fan_action('off')
                        logging.info("Fan turned off.")
                        # for command_file in command_files:
                        #     if os.path.exists(command_file):
                        #         with open(command_file, 'w') as f:
                        #             f.write(json.dumps({'action': 'action', 'message': '[TURN_OFF_FAN]'}))
                else:
                    # DHT['error_code'] = result.error_code
                    # print(f"DHT11 Error: {result.error_code}")
                    print("Failed to retrieve data from sensor")
                    DHT['error_code'] = 'Read failed'
                    try:
                        DHT['sys_temp'] = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True,
                                                         check=True).stdout.strip().split('=')[1]
                        # System Temp.: 46.2'C
                        # remove the 'C
                        DHT['sys_temp'] = DHT['sys_temp'].replace('\'C', '')
                        IoTHttp().update(IoTHttp().tag['TEMP'], DHT['sys_temp'])
                    except Exception as e:
                        logging.error(f"Error retrieving system temperature: {e}")

                if current_mode == "menu":
                    render_menu()
            except RuntimeError as error:
                logging.error(f"RuntimeError in DHT11 read thread: {error.args[0]}")
                time.sleep(2)
                continue
            time.sleep(2)

    except KeyboardInterrupt:
        logging.info("DHT11 read thread stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error in DHT11 read thread: {e}")
    finally:
        dht_device.exit()

def measure_distance():
    """
    Measure the distance using HC-SR04
    :return:
    """
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

def measure_average_distance():
    """
    Measure the average distance over 3 readings with 1-second intervals
    :return:
    """
    distances = []
    detect_duration = 1  # seconds
    for _ in range(3):
        dist = measure_distance()
        print(f"Dist: {dist}cm")
        distances.append(dist)
        time.sleep(detect_duration)
    average_distance = sum(distances) / len(distances)

    return average_distance

def alert_buzzer():
    # Alert Buzzer
    for _ in range(5):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.2)

def keep_measure_distance():
    """
    Guard Mode -> The distance sensor monitors every 1 second. If the average value over three readings is less than 50 cm (default), the alarm buzzer will sound.

    Automatic Mode -> Suitable for public automatic sensor doors, it detects someone approaching and automatically opens the door. Parameter adjustments may be required.
    :return:
    """
    try:
        global automatic_door_mode
        limit_distance = 50
        while True:
            cm = measure_average_distance()
            print("Average Distance : %.1f cm" % cm)
            if cm < limit_distance:
                if automatic_door_mode==2:
                    door_action('open')
                elif automatic_door_mode==1:
                    # alert
                    alert_buzzer()
                else:
                    # silent mode do nothing
                    pass
            else:
                if automatic_door_mode == 2:
                    door_action('close')


            time.sleep(1)  # Wait for 1 second before next measurement
    except KeyboardInterrupt:
        print("\nMeasurement stopped")

# Function to turn LED on
def door_led_on():
    """
    turn on the LED of door
    :return:
    """
    GPIO.output(DOOR_LED_PIN, GPIO.HIGH)
    print("LED is ON")

# Function to turn LED off
def door_led_off():
    """
    turn off the LED of door
    :return:
    """
    GPIO.output(DOOR_LED_PIN, GPIO.LOW)
    print("LED is OFF")
def door_action(action):
    if action == 'open':
        logging.info("Door opened.")
        door_led_on()
        GPIO.output(OPEN_DOOR_PIN, GPIO.HIGH)
        GPIO.output(CLOSE_DOOR_PIN, GPIO.LOW)
        print("Door is opening...")
        time.sleep(2)
        door_led_off()
    elif action == 'close':
        door_led_on()
        logging.info("Door closed.")
        GPIO.output(OPEN_DOOR_PIN, GPIO.LOW)
        GPIO.output(CLOSE_DOOR_PIN, GPIO.HIGH)
        print("Door is closing...")
        time.sleep(2)

        door_led_off()
def light_action(action):
    if action == 'on':
        logging.info("Light turned on.")
        door_led_on()
        GPIO.output(AI_LED_PIN, GPIO.HIGH)
        print("LED is ON")
    elif action == 'off':
        logging.info("Light turned off.")
        door_led_off()
        GPIO.output(AI_LED_PIN, GPIO.LOW)
        print("LED is OFF")
def fan_action(action):
    if action == 'on':
        logging.info("Fan turned on.")
        GPIO.output(FAN_PIN, GPIO.HIGH)
        print("Fan is ON")
    elif action == 'off':
        logging.info("Fan turned off.")
        GPIO.output(FAN_PIN, GPIO.LOW)
        print("Fan is OFF")

def ai_record_audio(filename):
    """
    Record audio from the microphone and save it to a WAV file.
    """
    logging.info(f"Recording started: {filename}")
    GPIO.output(AI_LED_PIN, GPIO.HIGH)  # Turn on LED to indicate recording
    try:
        recording = sd.rec(int(RECORD_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16')
        sd.wait()  # Wait until recording is finished
        wavio.write(filename, recording, SAMPLE_RATE, sampwidth=2)
        logging.info(f"Recording finished: {filename}")
        return True
    except Exception as e:
        logging.error(f"Error recording audio: {e}")
        return False
    finally:
        GPIO.output(AI_LED_PIN, GPIO.LOW)  # Turn off LED after recording

def ai_send_audio_to_ai(audio_file_path):
    """
    Send the audio file to AI API for speech recognition and command parsing.
    """
    try:
        global role_system
        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()
            audio_data = base64.b64encode(audio_bytes).decode()

        # Define the input and output formats
        format_ = AUDIO_FORMAT
        bitrate = BITRATE

        # Create the API request
        completion = client.chat.completions.create(
            model="qwen2-72b",
            extra_body={
                "tts_audio_format": format_,
                "tts_audio_bitrate": bitrate,
                "require_audio": True,
                "tts_preset_id": "jessica",
            },
            messages=[
                role_system,
                {
                    "role": "user",
                    "content": [{"type": "audio", "data": audio_data}]
                }
            ],
            max_tokens=50,
            temperature=0,
            stream=False  # Set stream to False as per your requirement
        )

        # Extract the command from the response
        if completion.choices and len(completion.choices) > 0:
            message_obj = completion.choices[0].message
            command_json_str = message_obj.content.strip()  # use content instead of message
            print(f"AI Response: {command_json_str}")  #  print AI response
            logging.info(f"AI Response: {command_json_str}")  # print AI response
            # Validate JSON
            try:
                command = json.loads(command_json_str)
                if 'action' in command and 'message' in command:
                    logging.info(f"Recognized command: {command}")
                    return command
                else:
                    logging.warning("AI response JSON does not contain 'action' and 'message' fields.")
                    return {"action": "unknown", "message": ""}
            except json.JSONDecodeError:
                logging.error("AI response is not valid JSON.")
                return {"action": "unknown", "message": ""}
        else:
            logging.warning("No command recognized from AI API.")
            return {"action": "unknown", "message": ""}

        # Extract the command from the response
        # if completion.choices and len(completion.choices) > 0:
        #     command = completion.choices[0].message['content'].strip()
        #     logging.info(f"Recognized command: {command}")
        #     return command
        # else:
        #     logging.warning("No command recognized from AI API.")
        #     return "[UNKNOWN_COMMAND]"

    except Exception as e:
        logging.error(f"Error sending audio to AI API: {e}")
        return {"action": "unknown", "message": ""}

def ai_write_command(command):
    """
    Write the command to the command file in JSON format.
    """
    try:
        global command_files
        for command_file in command_files:
            if os.path.exists(command_file):
                with open(command_file, "w") as file:
                    json.dump(command, file)
        logging.info(f"Command written to file: {command}")
    except Exception as e:
        logging.error(f"Error writing command to file: {e}")

def ai_process_audio_file(audio_directory, filename):
    """
    Process a single audio file: send to AI and write the command.
    """
    audio_path = os.path.join(audio_directory, filename)
    logging.info(f"Processing audio file: {audio_path}")
    command = ai_send_audio_to_ai(audio_path)
    # ai_write_command(command)
    # we don't need to write the command to file, just call it
    if command['action'] == 'unknown':
        logging.warning("Unknown command received.")
    else:
        global automatic_door_mode
        cmd = command['action']
        payload = command['message']
        if cmd == '[OPEN_DOOR]':
            door_action('open')
        elif cmd == '[CLOSE_DOOR]':
            door_action('close')
        elif cmd == '[TURN_ON_LIGHT]':
            light_action('on')
        elif cmd == '[TURN_OFF_LIGHT]':
            light_action('off')
        elif cmd == '[TURN_ON_FAN]':
            fan_action('on')
        elif cmd == '[TURN_OFF_FAN]':
            fan_action('off')
        elif cmd == '[GUARD_MODE]':
            automatic_door_mode = 1
            logging.info("Guard mode activated.")
        elif cmd == '[AUTOMATIC_MODE]':
            automatic_door_mode = 2
            logging.info("Automatic mode activated.")
        elif cmd == '[Silent_Mode]':
            automatic_door_mode = 3
            logging.info("Silent mode activated.")
        else:
            logging.warning(f"Unknown command: {cmd}")

    # Optionally, move or delete the processed audio file
    try:
        os.remove(audio_path)
        logging.info(f"Processed and removed audio file: {audio_path}")
    except Exception as e:
        logging.error(f"Error removing audio file '{audio_path}': {e}")

def ai_monitor_button_and_record(audio_directory):
    """
    Monitor the button and record audio when the button is pressed.
    """
    try:
        while True:
            button_state = GPIO.input(AI_BUTTON_PIN)
            if button_state == GPIO.LOW:
                # Button pressed
                timestamp = int(time.time())
                filename = f"audio_{timestamp}.wav"
                audio_path = os.path.join(audio_directory, filename)
                success = ai_record_audio(audio_path)
                if success:
                    ai_process_audio_file(audio_directory, filename)
                # Debounce to prevent multiple recordings
                time.sleep(1)
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("command_writer.py terminated by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        GPIO.cleanup()

def ai_main():
    AUDIO_DIRECTORY = "/home/terry/audio_files"  # Replace with your actual audio files directory

    if not os.path.exists(AUDIO_DIRECTORY):
        os.makedirs(AUDIO_DIRECTORY)
        logging.info(f"Created audio directory: {AUDIO_DIRECTORY}")

    logging.info("Starting command_writer.py...")
    GPIO.output(AI_LED_PIN, GPIO.LOW)  # Turn off LED
    # Start monitoring the button and recording audio in the main thread
    ai_monitor_button_and_record(AUDIO_DIRECTORY)

# Function to Process Commands from Queue
# def process_commands():
#     while True:
#         if not command_queue.empty():
#             cmd, payload = command_queue.get()
#             if cmd == 'display':
#                 update_display(msg=payload)
#                 set_mode_action()
#             elif cmd == 'clear':
#                 clear_display()
#                 set_mode_action()
#             elif cmd == 'qr_code':
#                 qr_code_btn()
#                 set_mode_action()
#         time.sleep(0.1)
def process_commands():
    while True:
        if not command_queue.empty():
            cmd, payload = command_queue.get()
            if cmd == 'display':
                # # update_display(msg=payload)
                # lines = payload.split('\n')
                # logging.info(f"Processed command: display '{payload}'")
                global scroll_context
                # scroll_context = ScrollContext(content_lines=lines)
                # render_scrolling_display()
                # # render_menu()  # Display "<- Back"

                message = payload

                wrapped_lines = []
                for line in message.split('\n'):
                    wrapped_lines.extend(wrap_text(line, device.width // char_width))

                scroll_context = ScrollContext(content_lines=wrapped_lines)

                render_scrolling_display()
                logging.info(f"Processed command: display '{payload}'")
            elif cmd == 'clear':
                global current_mode
                clear_display()
                logging.info("Processed command: clear")
                current_mode = "menu"
                scroll_context = None
                render_menu()
            elif cmd == 'qr_code':
                qr_code_btn()
                logging.info("Processed command: show qr code")
                set_mode_action()
                # render_menu()  # Display "<- Back"
            elif cmd == 'door':
                door_action(payload)
                logging.info(f"Processed command: door '{payload}'")
            elif cmd == 'light':
                light_action(payload)
                logging.info(f"Processed command: light '{payload}'")
            elif cmd == 'fan':
                fan_action(payload)
                logging.info(f"Processed command: fan '{payload}'")

        time.sleep(0.1)

# Function to Initialize and Render Menu
def initialize_menu():
    global IP,BT

    backlight.on()  # Ensure backlight is on before initializing the menu
    time.sleep(0.1)
    backlight.off()
    time.sleep(0.1)
    backlight.on()
    time.sleep(0.1)

    # hostname -I
    # example: 192.168.50.254 192.168.0.1 fd3a:cce6:35f6:b144:ba27:ebff:fe92:556a fd3a:cce6:35f6:b144:1453:384:c821:781
    result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, check=True)
    IP = result.stdout.split()[0]
    # bluetoothctl show
    # get Powered and Discoverable
    # example: Powered: yes Discoverable: yes

    result = subprocess.run(['bluetoothctl', 'show'], capture_output=True, text=True, check=True)


    for line in result.stdout.split('\n'):
        parts = line.strip().split(': ')
        if len(parts) == 2:
            BT[parts[0].strip()] = parts[1].strip()

    calculate_screen_size() # this will set char_width and char_height,must be exist
    time.sleep(0.1)

    render_menu()



# Initialize Menu and Render Initial Display
initialize_menu()
# Start Threads for Command Checking and Processing
threading.Thread(target=check_lcd_command, daemon=True).start()
threading.Thread(target=process_commands, daemon=True).start()
threading.Thread(target=dht11_read, daemon=True).start()
threading.Thread(target=keep_measure_distance, daemon=True).start()
threading.Thread(target=ai_main, daemon=True).start()
print("Menu system initialized. Waiting for button presses...")
pause()
