
import threading
import time
import os
import random


def wait_for_device(device, timeout=30):
    start_time = time.time()
    while not os.path.exists(device):
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for {device} to be created.")
            return False
        time.sleep(1)
    return True

def send_verification_code(device, message):
    try:
        with open(device, 'w', encoding='utf-8') as rfcomm:
            rfcomm.write(message + '\0')
            rfcomm.flush()
        print(f"Device B sent: {message}")
    except Exception as e:
        print(f"Error writing to {device}: {e}")

def receive_data(device):
    buffer = ''
    try:
        with open(device, 'r', encoding='utf-8', errors='ignore') as rfcomm:
            while True:
                char = rfcomm.read(1)
                if not char:
                    time.sleep(0.1)
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
    verification_code_b =  str(random.randint(100000, 999999))
    handshake_successful = False

    def sender():
        while not handshake_successful:
            send_verification_code(device_send, verification_code_b)
            time.sleep(1)

    sender_thread = threading.Thread(target=sender, daemon=True)
    sender_thread.start()

    data_generator = receive_data(device_receive)
    while not handshake_successful:
        try:
            data = next(data_generator)
            data_filtered = ''.join(filter(lambda x: x.isprintable(), data)).strip()
            print(f"Device B received: {data_filtered}")

            if data_filtered == "ready":
                handshake_successful = True

            elif len(data_filtered)==6 and data_filtered == verification_code_b:
                send_verification_code(device_send, "ready")
                send_verification_code(device_send, "ready")
                send_verification_code(device_send, "ready")
                send_verification_code(device_send, "ready")
                send_verification_code(device_send, "ready")
                print("Handshake completed. Device B is ready.")
            elif len(data_filtered) ==5:
                combined_code =  str(data_filtered) + str(verification_code_b)
                send_verification_code(device_send, combined_code)

        except StopIteration:
            break


    print("Device B received 'ready'. Handshake is fully completed.")




def main():
    device_send = '/dev/rfcomm1'  # Device B sends data on rfcomm1
    device_receive = '/dev/rfcomm0'  # Device B receives data on rfcomm0

    # Wait for devices to be available
    if not wait_for_device(device_send) or not wait_for_device(device_receive):
        print("Devices not available. Exiting.")
        return

    # Perform handshake
    handshake(device_send, device_receive)

    # Proceed to normal processing
    print("Device B entering normal operation.")

    # ... Rest of your code for normal processing ...

if __name__ == "__main__":
    main()