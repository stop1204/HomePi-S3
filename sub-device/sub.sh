#!/bin/bash
# terry@terry16:~/Desktop/bluetooth $ pwd
# /home/terry/Desktop/bluetooth


# Target keyword to match the device name
TARGET_NAME="terry-main"
MAC_ADDRESS=""
# Enable Bluetooth agent for automatic pairing (NoInputNoOutput)
{
      sleep 10
			echo "agent off"
			sleep 5
    	echo "agent NoInputNoOutput"
			sleep 5

} | bluetoothctl
bluetoothctl scan on &
scan_pid=$!
# Continuously check for the device until found
while [ -z "$MAC_ADDRESS" ]; do
    sleep 2  # Wait before checking again

    # Get the MAC address of the target device
    MAC_ADDRESS=$(bluetoothctl devices | grep -i "$TARGET_NAME" | awk '{print $2}')
    if [ -n "$MAC_ADDRESS" ]; then
        echo "Found device: $MAC_ADDRESS"
    else
        echo "Device containing keyword '$TARGET_NAME' not found. Continuing to scan..."
    fi
done
# Keep the script running
bluetoothctl scan off
kill $scan_pid  # Kill the background scanning process

# Device is found, now check if it's paired, trusted, and connected

# 1. Check if the device is paired

while true; do
paired=$(bluetoothctl devices Paired | grep "$MAC_ADDRESS")
if [ -z "$paired" ]; then

    echo "Device $MAC_ADDRESS is not paired. Pairing now..."
    echo "pair $MAC_ADDRESS" | bluetoothctl
    sleep 5
else

    echo "Device $MAC_ADDRESS is already paired."
    break
fi
done

while true; do
# 2. Check if the device is trusted
trusted=$(bluetoothctl devices Trusted | grep "$MAC_ADDRESS")
if [ -z "$trusted" ]; then
    echo "Device $MAC_ADDRESS is not trusted. Trusting now..."
    echo "trust $MAC_ADDRESS" | bluetoothctl
    sleep 5
else
    echo "Device $MAC_ADDRESS is already trusted."
    break
fi
done
while true; do
# 3. Check if the device is connected
connected=$(bluetoothctl devices Connected | grep "$MAC_ADDRESS")
if [ -z "$connected" ]; then
    echo "Device $MAC_ADDRESS is not connected. Connecting now..."
    echo "connect $MAC_ADDRESS" | bluetoothctl
    sleep 5
else
    echo "Device $MAC_ADDRESS is already connected."
    break
fi
done

while true; do
    echo "scan off"
    sleep 86400  # Sleep for 1 day
done

echo "sub.sh exit"

