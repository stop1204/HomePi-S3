# this is for test the IR(infrared receiver) sensor
# detect the running environment, if running on macOS use the GOIOzero library, otherwise use the RPi.GPIO library

import platform
from DeviceInfo import device_info
import time

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
                        signal = self.decode_ir_signal()  # virtual method
                        self.label_signal(signal)
                else:
                    self.pi.callback(self.pin, pigpio.FALLING_EDGE, self.ir_callback)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("IR signal listening stopped.")
        finally:
            if platform.system() != 'Darwin':
                self.pi.stop()  # cleanup pigpio resources

    def ir_callback(self, gpio, level, tick):
        # use pigpio to detect IR signal
        if level == pigpio.FALLING_EDGE:
            signal = self.decode_ir_signal()
            self.label_signal(signal)

    def decode_ir_signal(self):
        # virtual method to decode IR signal
        return int(time.time()) % 20  # use current time as a dummy signal

    def label_signal(self, signal):
        if 1 <= signal <= 10:
            print(f"Received signal: {signal}")
        else:
            print(f"Received signal: {signal}, labeled as 'others'")

# 主程序
if __name__ == "__main__":
    ir_receiver = IRReceiver(pin=17)  # assume the IR receiver is connected to GPIO 17
    ir_receiver.listen()