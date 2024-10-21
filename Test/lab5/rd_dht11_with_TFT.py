import time
import board
import adafruit_dht
import digitalio
from PIL import Image, ImageDraw
from PIL import ImageFont
import adafruit_rgb_display.st7735 as st7735

# Define constants to allow easy resizing of shapes
BORDER = 10
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

# Create blank image for drawing, (160 x 128)
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

image = Image.new("RGB", (width, height))

# Get drawing object to draw on image
draw = ImageDraw.Draw(image)

# Draw a green filled box as the background
draw.rectangle((0, 0, width, height), outline=GREEN, fill=GREEN)

#Draw a smaller inner purple rectangle
draw.rectangle((BORDER, BORDER, width-BORDER, height-BORDER-1), outline=MAGENTA, fill=MAGENTA)

# Load a TTF font
font = ImageFont.truetype("/user/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", FONTSIZE)

# Draw some text
# text = "Hello World!"
# (font_width, font_height) = font.getsize(text)
# draw.text(
#     (width // 2 - font_width // 2, height // 2 - font_height // 2),
#     text,
#     font=font,
#     fill=WHITE,
# )
# disp.image(image)

def draw_temp_humidity(temperature, humidity):
    # clear screen (purple rect.)
    draw.rectangle((BORDER, BORDER, width-BORDER, height-BORDER-1), outline=MAGENTA, fill=MAGENTA)

    text = f"Temp: {temperature} C"
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (width // 2 - font_width // 2, height // 2 - font_height // 2 -10),
        text,
        font=font,
        fill=WHITE,
    )
    text = f"Humidity: {humidity} %"
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (width // 2 - font_width // 2, height // 2 - font_height // 2 + 10),
        text,
        font=font,
        fill=WHITE,
    )


    disp.image(image)


# init sensor, use GPIO 26
dht_device = adafruit_dht.DHT11(board.D2)

try:
    while True:
        # read temp&humidity
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        if humidity is not None and temperature is not None:
            draw_temp_humidity(temperature, humidity)
            print(time.strftime('%d/%m/%y')+" "+time.strftime('%H:%M')+"\tTemp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
        #print("Temperature: %d C" % result.temperature)
        #print("Humidity: %d %%" % result.humidity)
        else:
            print("Failed to retrieve data from sensor")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped by User")
except RuntimeError as error:
    # process error
    print(f"RuntimeError: {error.args[0]}")
    time.sleep(2)
