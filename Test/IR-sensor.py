# this is for test the IR(infrared receiver) sensor
# detect the running environment, if running on macOS use the GOIOzero library, otherwise use the RPi.GPIO library

import platform
from Library.DeviceInfo import device_info
import time
import sys
import os

# add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if platform.system() == 'Darwin':
    from gpiozero import DigitalInputDevice  # remote GPIO for macOS
    from gpiozero.pins.pigpio import PiGPIOFactory
    print("Running on macOS, using gpiozero.")
elif platform.system() == 'Linux':
    import pigpio  # local GPIO for Raspberry Pi
    print("Running on Raspberry Pi, using pigpio.")

class IRReceiver:
    def __init__(self, pin):
        self.pin = pin
        if platform.system() == 'Darwin':
            self.factory = PiGPIOFactory(host=device_info.get_host_ip())
            self.ir_sensor = DigitalInputDevice(pin,pin_factory=self.factory)
        else:
            self.pi = pigpio.pi()  # 初始化 pigpio
            if not self.pi.connected:
                raise RuntimeError("Failed to connect to pigpio daemon.")
            self.pi.set_mode(pin, pigpio.INPUT)
            self.last_tick = 0

    def listen(self):
        print("Listening for IR signals...")

        try:
            while True:
                if platform.system() == 'Darwin':
                    if self.ir_sensor.is_active:
                        signal = self.decode_ir_signal()  # 模擬信號解碼
                        self.label_signal(signal)
                else:
                    self.pi.callback(self.pin, pigpio.FALLING_EDGE, self.ir_callback)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("IR signal listening stopped.")
        finally:
            if platform.system() != 'Darwin':
                self.pi.stop()  # 結束 pigpio 會話

    def ir_callback(self, gpio, level, tick):
        # 使用 pigpio 在 Raspberry Pi 上處理 IR 信號
        if level == pigpio.FALLING_EDGE:
            signal = self.decode_ir_signal()
            self.label_signal(signal)

    def decode_ir_signal(self):
        # 模擬解碼邏輯，實際情況中需要實現具體的信號解碼邏輯
        return int(time.time()) % 20  # 使用時間模擬信號變化，返回 1 到 20 的值

    def label_signal(self, signal):
        if 1 <= signal <= 10:
            print(f"Received signal: {signal}")
        else:
            print(f"Received signal: {signal}, labeled as 'others'")

# 主程序
if __name__ == "__main__":
    ir_receiver = IRReceiver(pin=17)  # 假設 IR 接收器連接到 GPIO 17 引腳
    ir_receiver.listen()