#!/bin/bash
# script path ~/Desktop/bluetooth
# script path /home/terry/Desktop/bluetooth


# Stop any running Bluetooth scripts
#sudo systemctl stop bluetooth

# Start the Bluetooth service
#sudo systemctl start bluetooth

# Wait for the Bluetooth service to start


# Enable Bluetooth power
{
    sleep 10
    echo "agent off"
    sleep 5
    echo "agent NoInputNoOutput"
    sleep 5
} | bluetoothctl


# Wait for incoming connections
echo "Waiting for devices to connect..."


pair_and_trust() {
    local device_mac=$1
#    echo "paring: $device_mac"
#    bluetoothctl pair "$device_mac"
#    if [ $? -eq 0 ]; then
#        echo "succeed : $device_mac"
#    else
#        echo "Failed : $device_mac"
#        return 1
#    fi

    bluetoothctl trust "$device_mac"
    if [ $? -eq 0 ]; then
        echo "Trusted: $device_mac"
    else
        echo "Failed: $device_mac"
	return 1
    fi

#    bluetoothctl connect "$device_mac"
#    if [ $? -eq 0 ]; then
#        echo "Connected: $device_mac"
#	echo "scan off"
#	return 0
#    else
#        echo "Failed: $device_mac"
#	return 1
#    fi
}

# Keep the script running to maintain the connection
succeed_msg="Connected: yes"
while true; do
  break
    devices=$(bluetoothctl devices | grep Device | awk '{print $2}')
    doExit=$1
    keyword="terry"
    for mac in $devices; do

    	device_name=$(bluetoothctl info "$mac" | grep "Name" | awk '{print $2}')
	      if [[ "$device_name" != *"$keyword"* ]]; then
            # echo "Device $mac does not contain the keyword, skipping..."
            continue
        fi

       # paired=$(bluetoothctl device | grep "$mac")
        trusted=$(bluetoothctl info "$mac" | grep "Trusted: yes")
	      connected=$(bluetoothctl info "$mac" | grep "Connected: yes")
        if [[ -n "$mac" ]]; then
            if [[ -z "$trusted" ]]; then
                echo "found new device: $mac"
                pair_and_trust "$mac"
	            	doExit=$?
            else
                if [[ "$connected" ]]; then

               	 echo "Connected: $mac"
		            doExit=0
		            else
		               echo "Connecting: $mac"
                	  output=$(bluetoothctl connect "$mac")

                	 if echo "$output" | grep -q "$success_msg"; then
                           echo "Successfully connected to $device_mac"
                           doExit=0
                           break  # Exit the loop if connected
                       else
                           echo "Failed to connect. Retrying in 3 seconds..."
                           doExit=1
                           sleep 3  # Wait for a few seconds before retrying
                       fi
             	  fi
            fi
        fi
        echo "-------------$doExit"
				if [[ -n "$doExit"  && "$doExit" -eq 0 ]]; then
			   	 break  # Exit the loop
				fi
    done
				if [[ -n "$doExit"  && "$doExit" -eq 0 ]]; then
                                 break  # Exit the loop
                                fi
sleep 5
done
#echo "scan off"
#wait
while true; do
        sleep 86400
done
echo "main.sh exit"
exit 0
