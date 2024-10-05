#!/bin/bash
# kill print.py and run it again without sudo permissions

pids=$(pgrep -f "speech_handler.py")

if [ -z "$pids" ]; then
    echo "cannot find speech_handler.py"
else
    echo "kill: $pids"
    kill -9 $pids
    echo "stopped"
fi

sleep 1
echo "running speech_handler.py"

# Set environment variables for Azure Speech
export SPEECH_KEY=c993ba5df13f4086aa3c6c49f0ba55e1
export SPEECH_REGION=japaneast

# Run the Python script without sudo
pwd
python3 /home/terry/Desktop/HomePi-S3/main-device/speech_handler.py &
wait