# This script tests the IR (infrared receiver) sensor.
# It detects the running environment; if running on macOS, it connects to the pigpio daemon on the Raspberry Pi.
# If running on Linux (Raspberry Pi), it uses the local pigpio library.

import platform
import time
from DeviceInfo import device_info  # Assumed to provide device_info.get_host_ip()
import pigpio

import lirc

lirc.init("test")
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
        # Thresholds in microseconds
        LEADER_HIGH_MIN = 8500
        LEADER_HIGH_MAX = 9500
        LEADER_LOW_MIN = 4000
        LEADER_LOW_MAX = 5000
        BIT_MARK_MIN = 500
        BIT_MARK_MAX = 700
        ZERO_SPACE_MIN = 400
        ZERO_SPACE_MAX = 700
        ONE_SPACE_MIN = 1500
        ONE_SPACE_MAX = 1900
        # Remove the initial gap if present
        if code[0] > 100000:
            code = code[1:]
        # Check for leader code
        if len(code) < 2:
            print("Code too short to process.")
            return
        leader_high = code[0]
        leader_low = code[1]
        if not (LEADER_HIGH_MIN <= leader_high <= LEADER_HIGH_MAX and LEADER_LOW_MIN <= leader_low <= LEADER_LOW_MAX):
            print("Leader code not detected.")
            return
        # Process bits
        bits = []
        i = 2  # Start after leader code
        while i < len(code) - 1:
            mark = code[i]
            space = code[i + 1]
            if not (BIT_MARK_MIN <= mark <= BIT_MARK_MAX):
                print(f"Invalid mark duration at index {i}: {mark}")
                return
            if ZERO_SPACE_MIN <= space <= ZERO_SPACE_MAX:
                bits.append('0')
            elif ONE_SPACE_MIN <= space <= ONE_SPACE_MAX:
                bits.append('1')
            else:
                print(f"Invalid space duration at index {i+1}: {space}")
                return
            i += 2
        # Check if we have 32 bits
        if len(bits) != 32:
            print(f"Expected 32 bits, got {len(bits)} bits.")
            return
        # Convert bits to bytes
        address_bits = bits[0:8]
        address_inv_bits = bits[8:16]
        command_bits = bits[16:24]
        command_inv_bits = bits[24:32]
        address = int(''.join(address_bits), 2)
        address_inv = int(''.join(address_inv_bits), 2)
        command = int(''.join(command_bits), 2)
        command_inv = int(''.join(command_inv_bits), 2)
        # Verify the data
        if address ^ address_inv != 0xFF or command ^ command_inv != 0xFF:
            print("Data verification failed.")
            return
        print(f"Decoded Address: {hex(address)}")
        print(f"Decoded Command: {hex(command)}")

    def cancel(self):
        self.cb.cancel()

# Main program
if __name__ == "__main__":
    ir_receiver = IRReceiver(pin=17)  # Assume the IR receiver is connected to GPIO 17
    ir_receiver.listen()