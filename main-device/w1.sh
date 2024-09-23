#!/bin/bash
# /home/terry/Desktop/transmit/w1.sh
# chmod +x /home/terry/Desktop/transmit/w1.sh
# /home/terry/Desktop/HomePi-S3/main-device/w1.sh
# chmod +x /home/terry/Desktop/HomePi-S3/main-device/w1.sh
sudo rfcomm release /dev/rfcomm1
sudo rfcomm watch /dev/rfcomm1 3