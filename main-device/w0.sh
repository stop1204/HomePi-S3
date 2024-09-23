#!/bin/bash
# /home/terry/Desktop/transmit/w0.sh
# chmod +x /home/terry/Desktop/transmit/w0.sh
# /home/terry/Desktop/HomePi-S3/main-device/w0.sh
# chmod +x /home/terry/Desktop/HomePi-S3/main-device/w0.sh
sudo rfcomm release /dev/rfcomm0
sudo rfcomm watch /dev/rfcomm0 1