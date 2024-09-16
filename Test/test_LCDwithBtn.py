from gpiozero import LED, Button
from signal import pause


# GPIO distributed on BCM
BACKLIGHT_PIN = 18
BUTTON_PIN = 17

# init LED and Button
backlight = LED(BACKLIGHT_PIN)
button = Button(BUTTON_PIN)

# backlight on
backlight.on()
print("backlight on")

# 定義切換函數
def toggle_backlight():
    if backlight.is_lit:
        backlight.off()
        print("backlight off")
    else:
        backlight.on()
        print("backlight on")

# bind button event
button.when_pressed = toggle_backlight

print("press button to toggle backlight")

# keep the script running
pause()