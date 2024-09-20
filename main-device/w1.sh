#!/bin/bash
# /home/terry/Desktop/transmit/w1.sh
sudo rfcomm release /dev/rfcomm1
sudo rfcomm watch /dev/rfcomm1 3