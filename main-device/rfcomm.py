import os
import time
import subprocess

def get_connected_device():
    while True:
        result = subprocess.run(['bluetoothctl', 'devices', 'Connected'], capture_output=True, text=True)
        if result.stdout:
            lines = result.stdout.splitlines()
            if lines:
                return lines[0].split()[1]
        print("No connected devices found. Retrying in 3 seconds...")
        time.sleep(3)

def send_data(device, data):
    with open(device, 'w') as rfcomm:
        rfcomm.write(data)
    print(f"Sent from A: {data}")

def receive_data(device):
    result = subprocess.run(['dd', f'if={device}', 'bs=1', 'count=1'], capture_output=True)
    received_data = result.stdout
    print(f"Received by A: {received_data}")
    return received_data

def wait_for_feedback(device):
    while True:
        feedback = receive_data(device)
        if feedback:
            return feedback

def clear_buffer(device):
    consecutive_ones = 0
    while consecutive_ones < 10:
        data = receive_data(device)
        if len(data) == 1:
            consecutive_ones += 1
        else:
            consecutive_ones = 0
        time.sleep(0.1)

def main():
    rfcomm0 = '/dev/rfcomm0'  # Send data
    rfcomm1 = '/dev/rfcomm1'  # Receive data

    bt_address = get_connected_device()  # Loop until a connected device is found
    print(f"Connected to device: {bt_address}")

    # Establish connection to device B
    os.system(f'sudo rfcomm connect {rfcomm0} {bt_address} 1')
    os.system(f'sudo rfcomm connect {rfcomm1} {bt_address} 3')

    # Initial handshake to confirm connection
    send_data(rfcomm0, "A")  # Send a single byte 'A' from device A
    feedback = wait_for_feedback(rfcomm1)  # Wait for feedback from device B

    if feedback:
        print("Handshake successful! Starting buffer clearing...")
        clear_buffer(rfcomm1)  # Clear buffer

if __name__ == "__main__":
    main()
