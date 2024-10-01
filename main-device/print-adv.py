import io
import json
import string
import subprocess

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


# GPIO Configuration using gpiozero
BACKLIGHT_PIN = 18      # Backlight controlled via GPIO 18
BUTTON_UP_PIN = 20      # Yellow-Up (GPIO 20)
BUTTON_LEFT_PIN = 17    # Red-Left (GPIO 17)
BUTTON_RIGHT_PIN = 16   # Green-Right (GPIO 16)
BUTTON_DOWN_PIN = 21    # Blue-Bottom (GPIO 21)

# Initialize Backlight LED
backlight = LED(BACKLIGHT_PIN)
# backlight.on() will be called before initialize_menu()

# Initialize Buttons
button_up = Button(BUTTON_UP_PIN)        # Yellow-Up
button_left = Button(BUTTON_LEFT_PIN)    # Red-Left
button_right = Button(BUTTON_RIGHT_PIN)  # Green-Right
button_down = Button(BUTTON_DOWN_PIN)    # Blue-Bottom

# Initialize LCD
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, bus_speed_hz=36000000)
device = st7735(serial, width=160, height=128, rotate=1)
time.sleep(0.2)

# Initialize Character Dimensions
char_width, char_height = 0, 0

# setup logging
LOG_FILE = "operation.log"
IP = "0.0.0.0"
BT = {}

current_display_mode = "menu"  # ["menu","action", "scrolling"]
scrolling_context = None

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
            set_mode_action()

    def back(self):
        global current_mode
        if current_mode == "action":
            # Return to menu from action
            current_mode = "menu"
            render_menu()
        else:
            if self.history:
                self.current, self.selected_index = self.history.pop()
                render_menu()

    def get_display_items(self):
        return [item.title for item in self.current.children]

class ScrollingContext:
    def __init__(self, content_lines, reverse_order=False):
        if reverse_order:
            content_lines = list(reversed(content_lines))
        self.content_lines = content_lines
        self.total_lines = len(content_lines)
        self.current_scroll_index = 0
        self.lines_per_page = (device.height - 2 * char_height) // char_height  # 保留第一行状态和最后一行指令

    def scroll_up(self):
        if self.current_scroll_index > 0:
            self.current_scroll_index -= 1
            logging.info(f"Scrolled up to line {self.current_scroll_index}")

    def scroll_down(self):
        if self.current_scroll_index < self.total_lines - self.lines_per_page:
            self.current_scroll_index += 1
            logging.info(f"Scrolled down to line {self.current_scroll_index}")

    def get_visible_lines(self):
        return self.content_lines[self.current_scroll_index:self.current_scroll_index + self.lines_per_page]

# Initialize Command Queue
command_queue = Queue()

# Global variable to manage current mode
current_mode = "menu"  # can be "menu" or "action"

# Define Menu Actions
def display_device_status():
    global IP,BT
    status = (f"Device Status:\n- Backlight: On\n- Buttons: Active\n- LCD: Working"
              f"\n- IP:{IP}"
              f"\n- Bluetooth:"
              f"\n  - Name: {BT.get('Name', 'Unknown')}"
              f"\n  - Powered: {BT.get('Powered', 'Unknown')}"
              f"\n  - Discoverable: {BT.get('Discoverable', 'Unknown')}")
    update_display(msg=status)
    logging.info("Displayed device status.")
    set_mode_action()
    # render_menu()  # Display "<- Back"

def clear_screen():
    clear_display()
    logging.info("Cleared the display.")
    set_mode_action()
    # render_menu()  # Display "<- Back"

def show_qr_code():
    qr_code_btn()
    logging.info("Displayed QR code.")
    set_mode_action()
    # render_menu()  # Display "<- Back"

# def display_custom_message():
#     update_display("Custom Message!")
#     logging.info("Displayed custom message.")
# Define Menu Actions
def display_custom_message():
    message = "Hello, World!"
    update_display(msg=message)
    logging.info(f"Displayed message: '{message}'")
    set_mode_action()
    # render_menu()  # Display "<- Back"

def display_console_logs():
    if not os.path.exists(LOG_FILE):
        update_display("No logs available.")
        logging.warning("Attempted to display logs, but log file does not exist.")
    else:
        with open(LOG_FILE, 'r') as log_file:
            logs = log_file.read()
        update_display(msg=logs)
        logging.info("Displayed console logs.")
    set_mode_action()
    # render_menu()  # Display "<- Back"


# Create Menu Structure
root_menu = MenuItem("Main Menu", children=[
    MenuItem("Display Message", action=lambda: display_custom_message()),
    MenuItem("Show Web Addr.", action=show_qr_code),
    MenuItem("Device Status", action=display_device_status),
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
def get_tunnel_url(file_path="../nohup.out"):
    if not os.path.exists(file_path):
        print("Tunnel URL file not found.")
        return None
    with open(file_path, 'r') as file:
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
    image = Image.new("RGB", (device.width, device.height), ColorPalette.BLACK.value)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    print(f"mode: {current_mode}")
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
        instruction = "Select ->"
    draw.text((0, device.height - char_height), instruction, font=font, fill=ColorPalette.CYAN.value)
    # elif current_mode == "action":
    #     # In action mode, just display the action content and "<- Back"
    #     # Assuming the action has already updated the display
    #     draw.text((0, device.height - char_height), "<- Back", font=font, fill=ColorPalette.CYAN.value)

    device.display(image)
    print("Menu rendered")

# Function to Handle Menu Actions
def handle_menu_action(action):
    if callable(action):
        action()
        set_mode_action()
        render_menu()  # Ensure the back instruction is displayed
def button_back_pressed():
    print("Red-Left pressed")
    menu.back()
    render_menu()  # Ensure the menu or action screen is rendered correctly

# Button Press Handlers
def button_up_pressed():
    if current_mode == "menu":
        print("Yellow-Up pressed")
        menu.navigate_up()

def button_down_pressed():
    if current_mode == "menu":
        print("Blue-Bottom pressed")
        menu.navigate_down()

def button_select_pressed():
    if current_mode == "menu":
        print("Green-Right pressed")
        menu.select()

def button_back_pressed():
    print("Red-Left pressed")
    menu.back()

# Bind Button Events to Handlers
button_up.when_pressed = button_up_pressed
button_down.when_pressed = button_down_pressed
button_right.when_pressed = button_select_pressed
button_left.when_pressed = button_back_pressed

# Function to Check and Queue External Commands
def check_lcd_command():
    command_files = ['/lcd_command.txt', '../lcd_command.txt']
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
                if action == 'display':
                    logging.info(f"External command: display '{message}'")
                    command_queue.put(('display', message))
                elif action == 'clear':
                    logging.info("External command: clear")
                    command_queue.put(('clear', ''))
                elif action == 'show qr code':
                    logging.info("External command: show qr code")
                    command_queue.put(('qr_code', ''))
        time.sleep(1)

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
                update_display(msg=payload)
                logging.info(f"Processed command: display '{payload}'")
                set_mode_action()
                # render_menu()  # Display "<- Back"
            elif cmd == 'clear':
                clear_display()
                logging.info("Processed command: clear")
                set_mode_action()
                # render_menu()  # Display "<- Back"
            elif cmd == 'qr_code':
                qr_code_btn()
                logging.info("Processed command: show qr code")
                set_mode_action()
                # render_menu()  # Display "<- Back"
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
    backlight.off()
    time.sleep(0.1)
    backlight.on()
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
    render_menu()

# Start Threads for Command Checking and Processing
threading.Thread(target=check_lcd_command, daemon=True).start()
threading.Thread(target=process_commands, daemon=True).start()

# Initialize Menu and Render Initial Display
initialize_menu()

print("Menu system initialized. Waiting for button presses...")
pause()