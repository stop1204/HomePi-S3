# HomePi-S3


`16/9/2024` RaspberryPi Project : Smart Security System(S3) Based on Raspberry Pi 

# 🍓📲 Deployment Guide Simplified

## Step 1: 🛠️ Prepare the Raspberry Pi

Ensure you are using a Respberry Pi 3 Model B+ or newer.

## Step 2: ⚙️ Install Dependencies

Run the following commands to set up the necessary environment:
```
sudo apt install -y git python3 python3-pip python3-venv bluetooth bluez net-tools
cd ~/Desktop/
git clone https://github.com/stop1204/HomePi-S3.git
cd HomePi-S3
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
[//]: # (chmod +x natapp)
sudo chmod -R 777 .
```

## Step 3: ⚙️ Configure Startup

To ensure the system automatically starts the required components, use the configuration files provided in the project. The necessary startup configurations are already included, so simply follow these steps:

1. Use Provided ***`rc.local`*** Configuration:
The project includes a pre-configured `rc.local` file to handle the startup process automatically. Copy the provided `rc.local` to `/etc/rc.local` on your 🍓📲.

2. 📝 Explanation of Startup Scripts:

* `app.py`: 📜 Main application script that runs the core functionality.
* `natapp_monitor.sh`: 📜 Shell script to monitor and manage the natapp tunnel.

* `print.py`: 🖨️ Handles printing operations, also known as print.py.

* `rc.local`: ⚙️ The startup script executed at boot to set up the system environment. It performs the following:

* Exports required environment variables (`SPEECH_KEY`, `SPEECH_REGION`, etc.).

* Starts the `natapp` tunnel and redirects logs.
 
* Runs Bluetooth initialization (`main.sh`).
 
* Launches `app.py` for WiFi configurator and main application.
 
* Handles dynamic WiFi configuration (`nmcli` commands).
 
* Starts various helper scripts (`w0.sh`, `w1.sh`, `natapp_monitor.sh`).
 
* Logs startup events and network status.

## Step 4: 🚀 Start the Application manually or reboot the Raspberry Pi to start the application automatically.

To start the application, run the following command:
```
# kill any existing print.py processes
sudo kill -9 $(ps -ef | grep 'print.py' | awk '{print $2}')

# start the application
cd ~/Desktop/HomePi-S3/main-device/
./print.sh
```
