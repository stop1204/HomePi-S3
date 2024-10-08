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

for x in seg7:
    GPIO.setup(x, GPIO.OUT)
while True:
    for x in range(8):
        GPIO.output(seg7[x], 0) #turn off all segments
    for x in range(8):
        GPIO.output(seg7[x],1)
        time.sleep(0.5)