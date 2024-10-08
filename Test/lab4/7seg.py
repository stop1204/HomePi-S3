import time, RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# GPIO.setmode(GPIO.BCM)
#common cathode, common pin connected to ground
#pin connected to seg a

#g f a b  e d c dp
#BCM  21,20,16,12   6,4, 15,14
# seg_g = 21
# seg_f = 20
# seg_a = 16
# seg_b = 12
# seg_e = 6
# seg_d = 5
# seg_c = 15
# seg_dp = 14
seg_a = 5
seg_b = 33
seg_c = 19
seg_d = 15
seg_e = 13
seg_f = 7
seg_g = 21
seg_dp = 11

seg7 = [seg_a, seg_b, seg_c, seg_d, seg_e, seg_f, seg_g, seg_dp]

# number 1: b, c
# number 2: a, b, g, e, d
# number 3: a, b, g, c, d
# number 4: f, g, b, c
# number 5: a, f, g, c, d
# number 6: a, f, g, e, c, d
# number 7: a, b, c
# number 8: a, b, c, d, e, f, g
# number 9: a, b, c, f, g
# number 0: a, b, c, d, e, f
# dp: dp
def display_number(num):
    if num == 1:
        GPIO.output(seg_b, 1)
        GPIO.output(seg_c, 1)
    elif num == 2:
        GPIO.output(seg_a, 1)
        GPIO.output(seg_b, 1)
        GPIO.output(seg_g, 1)
        GPIO.output(seg_e, 1)
        GPIO.output(seg_d, 1)
    elif num == 3:
        GPIO.output(seg_a, 1)
        GPIO.output(seg_b, 1)
        GPIO.output(seg_g, 1)
        GPIO.output(seg_c, 1)
        GPIO.output(seg_d, 1)
    elif num == 4:
        GPIO.output(seg_f, 1)
        GPIO.output(seg_g, 1)
        GPIO.output(seg_b, 1)
        GPIO.output(seg_c, 1)
    elif num == 5:
        GPIO.output(seg_a, 1)
        GPIO.output(seg_f, 1)
        GPIO.output(seg_g, 1)
        GPIO.output(seg_c, 1)
        GPIO.output(seg_d, 1)
    elif num == 6:
        GPIO.output(seg_a, 1)
        GPIO.output(seg_f, 1)
        GPIO.output(seg_g, 1)
        GPIO.output(seg_e, 1)
        GPIO.output(seg_c, 1)
        GPIO.output(seg_d, 1)
    elif num == 7:
        GPIO.output(seg_a, 1)
        GPIO.output(seg_b, 1)
        GPIO.output(seg_c, 1)
    elif num == 8:
        GPIO.output(seg_a, 1)
        GPIO.output(seg_b, 1)
        GPIO.output(seg_c, 1)
        GPIO.output(seg_d, 1)
        GPIO.output(seg_e, 1)
        GPIO.output(seg_f, 1)
        GPIO.output(seg_g, 1)
    elif num == 9:
        GPIO.output(seg_a, 1)
        GPIO.output(seg_b, 1)
        GPIO.output(seg_c, 1)
        GPIO.output(seg_f, 1)
        GPIO.output(seg_g, 1)
    elif num == 0:
        GPIO.output(seg_a, 1)
        GPIO.output(seg_b, 1)
        GPIO.output(seg_c, 1)
        GPIO.output(seg_d, 1)
        GPIO.output(seg_e, 1)
        GPIO.output(seg_f, 1)
    elif num == -1:
        GPIO.output(seg_dp, 1)
    else:
        print("Invalid number")
        return

# Version 2
# for x in seg7:
#     GPIO.setup(x, GPIO.OUT)
# for x in range(8):
#     GPIO.output(seg7[x], 0) #turn off all segments
# while True:
#     for x in range(10):
#         display_number(x)
#         time.sleep(1)
#         # CLEAR DISPLAY
#         for x in range(8):
#             GPIO.output(seg7[x], 0) #turn off all segments
#
#     # DISPLAY DP, THIS IS THE PROMPT THAT WILL SET TO ZERO
#     display_number(-1)
#     time.sleep(1)


font = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x27, 0x7F, 0x6F, 0x00]
for x in seg7:
    GPIO.setup(x, GPIO.OUT)
def out(n): #function to convert decimal to binary
    for x in range(8):
        if n % 2 == 1: #check remainder
            GPIO.output(seg7[x], 1)
        else:
            GPIO.output(seg7[x], 0)
        n = n // 2 #get quotient

while True:
    # use font to display 0 ~ 9
    for i in range(10):
        out(font[i])
        time.sleep(0.5)
    # CLEAR DISPLAY
    for x in range(8):
        GPIO.output(seg7[x], 0)
    time.sleep(0.5)

# turn off all segments
# display digit 0 ~ 9 one by one, each displayed digit remains in 0.5s
