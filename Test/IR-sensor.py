# This script tests the IR (infrared receiver) sensor.
# It detects the running environment; if running on macOS, it connects to the pigpio daemon on the Raspberry Pi.
# If running on Linux (Raspberry Pi), it uses the local pigpio library.

import platform
import time
from DeviceInfo import device_info  # Assumed to provide device_info.get_host_ip()
import pigpio



class IRReceiver:
    def __init__(self, pin):
        self.pin = pin
        if platform.system() == 'Darwin':
            # Connect to the pigpio daemon on the Raspberry Pi
            self.pi = pigpio.pi(device_info.get_host_ip())
            if not self.pi.connected:
                raise RuntimeError("Failed to connect to pigpio daemon. (macOS)")
        else:
            # Initialize pigpio locally on Raspberry Pi
            self.pi = pigpio.pi()
            if not self.pi.connected:
                raise RuntimeError("Failed to connect to pigpio daemon.")
        # Set the pin as input
        self.pi.set_mode(self.pin, pigpio.INPUT)

        # Initialize variables for IR signal processing
        self.high_tick = 0
        self.gap = 10000  # Microseconds
        self.code_timeout = 50000  # Microseconds
        self.code = []
        self.in_code = False

        # Register the callback function
        self.cb = self.pi.callback(self.pin, pigpio.EITHER_EDGE, self.ir_callback)

    def listen(self):
        print("Listening for IR signals... Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("IR signal listening stopped.")
        finally:
            self.cancel()
            self.pi.stop()  # Clean up pigpio resources

    def ir_callback(self, gpio, level, tick):
        if level != pigpio.TIMEOUT:
            edge = tick
            if self.high_tick != 0:
                duration = pigpio.tickDiff(self.high_tick, edge)
                if duration > self.gap:
                    if self.in_code:
                        # Process the received code
                        self.process_code(self.code)
                        self.code = []
                    self.in_code = True
                if self.in_code:
                    self.code.append(duration)
            self.high_tick = edge
        else:
            # Timeout handling
            if self.in_code:
                self.process_code(self.code)
                self.code = []
                self.in_code = False

    def process_code(self, code):
        print("Received code:")
        print(code)
        # Add code decoding logic here

    def cancel(self):
        self.cb.cancel()

# Main program
if __name__ == "__main__":
    ir_receiver = IRReceiver(pin=17)  # Assume the IR receiver is connected to GPIO 17
    ir_receiver.listen()