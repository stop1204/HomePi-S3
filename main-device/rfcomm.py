import threading
import time
import os

import  random



def wait_for_device(device, timeout=30):
    start_time = time.time()
    while not os.path.exists(device):
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for {device} to be created.")
            return False
        time.sleep(1)
    return True

def send_verification_code(device, verification_code):
    try:
        with open(device, 'w', encoding='utf-8') as rfcomm:
            rfcomm.write(verification_code+'\0')
            rfcomm.flush()
        print(f"Device A sent verification code: {verification_code}")
    except Exception as e:
        print(f"Error writing to {device}: {e}")

def receive_data(device):
    buffer = ''
    try:
        with open(device, 'r', encoding='utf-8', errors='ignore') as rfcomm:
            while True:
                char = rfcomm.read(1)
                if not char:
                    # time.sleep(0.1)
                    continue
                buffer += char
                if '\0' in buffer:
                    data = buffer.strip()
                    buffer = ''
                    yield data
    except Exception as e:
        print(f"Error reading from {device}: {e}")
        yield ''


def handshake(device_send, device_receive):
    verification_code_a =  str( random.randint(10000, 99999))
    handshake_successful = False


    def sender():
        while not handshake_successful:
            send_verification_code(device_send, verification_code_a)
            time.sleep(0.5)

    sender_thread = threading.Thread(target=sender, daemon=True)
    sender_thread.start()

    data_generator = receive_data(device_receive)
    while not handshake_successful:
        try:
            data = next(data_generator)
            data_filtered = ''.join(filter(lambda x: x.isprintable(), data)).strip()
            print(f"Device A received: {data_filtered}")

            # A code length = 5  B code length = 6
            if len(data_filtered)==11 and  data_filtered.startswith(str(verification_code_a)):
                verification_code_b = data_filtered.lstrip(str(verification_code_a))
                send_verification_code(device_send, verification_code_b)
            elif data_filtered == "ready":
                send_verification_code(device_send, data_filtered)
                send_verification_code(device_send, data_filtered)
                send_verification_code(device_send, data_filtered)
                send_verification_code(device_send, data_filtered)
                send_verification_code(device_send, data_filtered)
                handshake_successful = True
                print("Handshake successful.")
        except StopIteration:
            break



    print("Handshake completed. Device A is ready.")

def main():
    device_send = '/dev/rfcomm0'  # Device A sends data on rfcomm0
    device_receive = '/dev/rfcomm1'  # Device A receives data on rfcomm1

    # Wait for devices to be available
    if not wait_for_device(device_send) or not wait_for_device(device_receive):
        print("Devices not available. Exiting.")
        return

    # Perform handshake
    handshake(device_send, device_receive)

    # Proceed to normal processing
    print("Device A entering normal operation.")

    # ... Rest of your code for normal processing ...

if __name__ == "__main__":
    main()
