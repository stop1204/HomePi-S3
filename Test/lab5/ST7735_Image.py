# sudo pip3 install adafruit-circuitpython-rgb-display --break-system-packages
import time
import digitalio
import board
from PIL import Image, ImageDraw
from PIL import ImageFont
import adafruit_rgb_display.st7735 as st7735

# Define constants to allow easy resizing of shapes
BORDER = 20
FONTSIZE = 12


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

# Create blank image for drawing
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

# Load an image.
print('Loading image...')
image = Image.open('cat.jpg')

# Resize the image and rotate it so matches the display.
image = image.rotate(0).resize((width, height))

# Draw the image on the display hardware.
print('Drawing image')
disp.image(image)