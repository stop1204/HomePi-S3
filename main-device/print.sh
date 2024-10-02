#!/bin/bash
# chmod +x print.sh
# kill print.py and run it again
pids=$(pgrep -f "print.py")

if [ -z "$pids" ]; then
    echo "cannot find print.py"
else
    echo "kill: $pids"
    kill -9 $pids
    echo "stopped"
fi

echo "running print.py"
python /home/terry/Desktop/HomePi-S3/main-device/print.py &
wait