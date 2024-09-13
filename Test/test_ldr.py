import RPi.GPIO as GPIO
import time

# 設置 GPIO 模式為 BCM
GPIO.setmode(GPIO.BCM)

# 定義使用的 GPIO 引腳
LDR_PIN = 17

# 設置引腳為輸入
GPIO.setup(LDR_PIN, GPIO.OUT)

def rc_time(pin):
    # 將引腳設置為低，讓電容放電
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)

    # 將引腳設置為輸入，開始測量充電時間
    GPIO.setup(pin, GPIO.IN)

    count = 0
    # 測量電容充電至高電平所需的時間
    while GPIO.input(pin) == GPIO.LOW:
        count += 1
        # 為了避免無限迴圈，添加一個最大計數
        if count > 100000:
            return count

    return count

try:
    while True:
        light_level = rc_time(LDR_PIN)
        print(f"光強度值（充電時間）：{light_level}")
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
    print("程式已終止並清理 GPIO 設置")