import time
import digitalio
import board
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7735 as st7735

# Define constants to allow easy resizing of shapes
BORDER = 20
FONTSIZE = 12

# Define Color for this display
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
BLUE    = (255,   0,   0)
GREEN   = (  0, 255,   0)
RED     = (  0,   0, 255)
CYAN    = (255, 255,   0)
MAGENTA = (255,   0, 255)
YELLOW  = (  0, 255, 255)

# Config for CS and DC pins
# cs_pin = digitalio.DigitalInOut(board.CE0)
# dc_pin = digitalio.DigitalInOut(board.D25)
# reset_pin = digitalio.DigitalInOut(board.D24)
cs_pin = digitalio.DigitalInOut(board.D8)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D18)

BAUDRATE = 24000000 #24MHz

# Setup SPI bus using hardware SPI
spi = board.SPI()

# Create the display
disp = st7735.ST7735R(
    spi,
    rotation=90,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE
)

# Create blank image for drawing, (160 x 128), landscape mode
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

#create an image object for display
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image
draw = ImageDraw.Draw(image)

# Draw a red ellipse with a green outline.
draw.ellipse((10, 10, 110, 80), outline=GREEN, fill=RED)

# Draw a white X.
draw.line((10, 80, 110, 120), fill=WHITE)
draw.line((10, 120, 110, 80), fill=WHITE)

# Draw a cyan polygon with a white outline.
draw.polygon([(120, 10), (150, 10), (135, 65), (150, 120), (120, 120)], outline=WHITE, fill=CYAN)

disp.image(image)   
