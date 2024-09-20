#!/bin/bash
# /home/terry/Desktop/transmit/w1.sh
# Function to get connected device MAC address
get_connected_device() {
    while true; do
        # Get the list of connected devices
        connected_devices=$(bluetoothctl devices Connected | awk '{print $2}')
        if [ -n "$connected_devices" ]; then
            echo "Connected device(s) found: $connected_devices"
            # If multiple devices are connected, use the first one
            mac_address=$(echo "$connected_devices" | head -n1)
            break
        else
            echo "No connected devices found. Retrying in 5 seconds..."
            sleep 5
        fi
    done
}

# Release rfcomm1 if it is already in use
sudo rfcomm release /dev/rfcomm1

# Get the MAC address of the connected device
get_connected_device

# Loop until successfully connected to /dev/rfcomm1 (channel 3)
while true; do
    echo "Attempting to connect to /dev/rfcomm1 with device $mac_address..."
    # Use process substitution to read the output of rfcomm connect
    sudo rfcomm connect /dev/rfcomm1 "$mac_address" 3 | while read -r line; do
        echo "$line"
        # Check if the line contains "Press" and "hangup"
        if [[ "$line" == *"Press"* && "$line" == *"hangup"* ]]; then
            echo "Connected successfully to /dev/rfcomm1."
            # Keep the script running to maintain the connection
            wait

        fi
    done
    echo "Connection failed, retrying in 5 seconds..."
    # Re-check connected devices in case the device has disconnected
    sleep 5
    get_connected_device
done
