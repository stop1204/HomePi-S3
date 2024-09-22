
import os
import subprocess
import time
import logging
import json
import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

log_path = os.path.join("/home","terry", "wifi_configurator", "wifi_configurator.log")
# log record
logging.basicConfig(
    filename=log_path,
    # filename='/tmp/wifi_configurator.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# path
WPA_SUPPLICANT_CONF = "/etc/wpa_supplicant/wpa_supplicant.conf"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wifi')
def wifi():
    return render_template('wifi_config.html')



def remove_ansi_escape(text):
    """
    Removes ANSI escape sequences from the given text.
    """
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def scan_wifi():
    try:
        result = subprocess.run(['sudo', 'iwlist', 'wlan0', 'scan'], capture_output=True, text=True, check=True)
        networks = []
        for line in result.stdout.split('\n'):
            if "ESSID:" in line:
                ssid = line.split("ESSID:")[1].strip().strip('"')
                if ssid:
                    networks.append(ssid)
        logging.debug(f"Scan network: {networks}")
        return list(set(networks))  # remove duplicate content
    except subprocess.CalledProcessError as e:
        logging.error(f"Scan Wi-Fi error: {e}")
        return []

def connect_wifi(ssid, password=None):
    try:
        logging.debug(f"try to connect to SSID: {ssid}，Password: {'Have' if password else 'None'}")

        # backup
        subprocess.run(['sudo', 'cp', WPA_SUPPLICANT_CONF, WPA_SUPPLICANT_CONF + ".bak"], check=True)
        logging.debug("back wpa_supplicant done")

        # create a new wpa_supplicant.conf
        with open(WPA_SUPPLICANT_CONF, 'w') as f:
            f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
            f.write('update_config=1\n')
            f.write('country=HK\n\n')
            f.write('network={\n')
            f.write(f'\tssid="{ssid}"\n')
            if password:
                # WPA-Enterprise
                f.write('\tkey_mgmt=WPA-EAP\n')
                f.write('\teap=PEAP\n')
                # f.write('\tidentity="terry"\n')  # username
                f.write('\tpassword="{}"\n'.format(password))
                f.write('\tphase2="auth=MSCHAPV2"\n')
                # ca certificate
                # f.write('\tca_cert="/path/to/ca-cert.pem"\n')
            else:
                f.write('\tkey_mgmt=NONE\n')
            f.write('}\n')
        logging.debug("wpa_supplicant.conf wrote")

        # re-config wpa_supplicant
        subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'], check=True)
        logging.debug("wpa_supplicant renew done")

        # sudo nmcli dev wifi connect "Your_SSID" password "Your_PASSWORD”
        result = subprocess.run(['sudo', 'nmcli', 'dev','wifi','connect',ssid,'password',password], capture_output=True, text=True)

        # wait
        time.sleep(10)
        if 'success' in result.stdout:
            return True
        else:
            logging.warning(f"Can't connect to Wi-Fi: {ssid}")
            return False
        # check connection
        result = subprocess.run(['iw', 'wlan0', 'link'], capture_output=True, text=True)
        if 'Not connected' not in result.stdout:
            logging.info(f"success connect to Wi-Fi: {ssid}")
            return True
        else:
            logging.warning(f"Can't connect to Wi-Fi: {ssid}")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"connect Wi-Fi fail: {e}")
        return False
    except Exception as e:
        logging.error(f"Unknow error: {e}")
        return False
def get_device_info():
    info = {}
    try:
        # Retrieve Wi-Fi information
        wifi_info = {}
        # Use nmcli to get the currently connected SSID
        wifi_result = subprocess.run(['nmcli', '-t', '-f', 'ACTIVE,SSID', 'dev', 'wifi'], capture_output=True, text=True)
        current_ssid = None
        for line in wifi_result.stdout.split('\n'):
            if line.startswith('yes:'):
                current_ssid = line.split(':')[1]
                break
        wifi_info['connected_ssid'] = current_ssid

        # Use nmcli to get more detailed Wi-Fi information
        if current_ssid:
            details = subprocess.run(['nmcli', '-t', '-f', 'all', 'connection', 'show', current_ssid], capture_output=True, text=True)
            for line in details.stdout.split('\n'):
                if line:
                    key, value = line.split(':', 1)
                    wifi_info[key.lower()] = value
        info['wifi'] = wifi_info

        # Retrieve Bluetooth information
        bluetooth_info = {}
        # Check Bluetooth adapter status
        bt_status = subprocess.run(['hciconfig'], capture_output=True, text=True)
        bluetooth_info['status'] = bt_status.stdout

        # Get paired Bluetooth devices
        paired_devices = subprocess.run(['bluetoothctl', 'devices', 'Paired'], capture_output=True, text=True)
        devices = []
        for line in paired_devices.stdout.split('\n'):
            #    if line:
            if line.startswith('Device '):
                parts = line.split(' ', 2)
                if len(parts) == 3:
                    devices.append({'address': parts[1], 'name': parts[2]})
        bluetooth_info['paired_devices'] = devices

        info['bluetooth'] = bluetooth_info

        logging.debug(f"Device Info: {info}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error retrieving device info: {e}")
    except Exception as e:
        logging.error(f"Unknown error retrieving device info: {e}")
    return info
def scan_bluetooth_old():
    """
    Scans for available Bluetooth devices and returns a list of devices.
    Each device is represented as a dictionary with 'address' and 'name'.
    """
    try:
        # Start scanning
        # this will block process
        subprocess.run(['bluetoothctl', 'scan', 'on'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.debug("Started Bluetooth scan.")

        # Wait for a few seconds to allow devices to be discovered
        time.sleep(5)

        # Stop scanning
        subprocess.run(['bluetoothctl', 'scan', 'off'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.debug("Stopped Bluetooth scan.")

        # Get the list of devices
        scan_output = subprocess.run(['bluetoothctl', 'devices'], capture_output=True, text=True)
        scan_output_clean = remove_ansi_escape(scan_output.stdout)

        devices = []
        for line in scan_output_clean.split('\n'):
            if line:
                parts = line.split(' ', 2)
                if len(parts) == 3:
                    address = parts[1]
                    name = parts[2]
                    devices.append({'address': address, 'name': name})

        logging.debug(f"Scanned Bluetooth devices: {devices}")
        return devices
    except subprocess.CalledProcessError as e:
        logging.error(f"Bluetooth scan failed: {e}")
        return []
    except Exception as e:
        logging.error(f"Unknown error during Bluetooth scan: {e}")
        return []
def scan_bluetooth():
    """
    Scans for available Bluetooth devices and returns a list of devices.
    Each device is represented as a dictionary with 'address' and 'name'.
    """
    try:
        # Start the Bluetooth scan by running 'bluetoothctl scan on' in a separate subprocess
        scan_process = subprocess.Popen(
            ['sudo', 'bluetoothctl', 'scan', 'on'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.debug("Started Bluetooth scan.")

        # Wait for a specified duration to allow devices to be discovered
        scan_duration = 5  # Duration in seconds
        time.sleep(scan_duration)

        # Stop the Bluetooth scan by running 'bluetoothctl scan off'
        #stop_scan = subprocess.run(
        #    ['sudo', 'bluetoothctl', 'scan', 'off'],
        #    check=True,
        #    stdout=subprocess.PIPE,
        #    stderr=subprocess.PIPE,
        #    text=True
        #)
        #logging.debug("Stopped Bluetooth scan.")

        # Terminate the scanning subprocess if it's still running
        if scan_process.poll() is None:
            scan_process.terminate()
            scan_process.wait(timeout=5)
            logging.debug("Terminated Bluetooth scan subprocess.")

        # Retrieve the list of paired and available Bluetooth devices
        scan_output = subprocess.run(
            ['sudo', 'bluetoothctl', 'devices'],
            capture_output=True,
            text=True,
            check=True
        )
        scan_output_clean = remove_ansi_escape(scan_output.stdout)
        logging.debug(f"Bluetooth devices output:\n{scan_output_clean}")

        devices = []
        for line in scan_output_clean.split('\n'):
            if line.startswith('Device '):
                parts = line.split(' ', 2)
                if len(parts) == 3:
                    address = parts[1]
                    name = parts[2]
                    devices.append({'address': address, 'name': name})

        logging.debug(f"Scanned Bluetooth devices: {devices}")
        return devices

    except subprocess.CalledProcessError as e:
        logging.error(f"Bluetooth scan failed: {e.stderr}")
        return []
    except subprocess.TimeoutExpired:
        scan_process.kill()
        logging.error("Bluetooth scan subprocess timed out and was terminated.")
        return []
    except Exception as e:
        logging.error(f"Unknown error during Bluetooth scan: {e}")
        return []
def connect_bluetooth(address):
    """
    Connects to a Bluetooth device given its MAC address.
    Returns True if the connection was successful, False otherwise.
    """
    try:
        logging.debug(f"Attempting to connect to Bluetooth device: {address}")

        # Initiate connection
        connect_result = subprocess.run(['bluetoothctl', 'connect', address], capture_output=True, text=True)
        connect_output_clean = remove_ansi_escape(connect_result.stdout)

        logging.debug(f"Bluetooth connect output: {connect_output_clean}")

        if "Connection successful" in connect_output_clean:
            logging.info(f"Successfully connected to Bluetooth device: {address}")
            return True
        else:
            logging.warning(f"Failed to connect to Bluetooth device: {address}")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Bluetooth connect failed: {e}")
        return False
    except Exception as e:
        logging.error(f"Unknown error during Bluetooth connect: {e}")
        return False

@app.route('/scan')
def scan():
    networks = scan_wifi()
    return jsonify(networks)

@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    ssid = data.get('ssid')
    password = data.get('password')
    success = connect_wifi(ssid, password)
    if success:
        #
        subprocess.run(['sudo', 'systemctl', 'stop', 'hostapd'], check=True)
        subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq'], check=True)
        logging.info("Connected Wi-Fi，Disable hostapd and dnsmasq")
        return jsonify({"status": "success"})
    else:
        logging.error("connect Wi-Fi fail")
        return jsonify({"status": "fail"}), 400

@app.route('/manual_connect', methods=['POST'])
def manual_connect():
    ssid = request.form.get('ssid')
    password = request.form.get('password')
    success = connect_wifi(ssid, password)
    if success:
        #
        subprocess.run(['sudo', 'systemctl', 'stop', 'hostapd'], check=True)
        subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq'], check=True)
        logging.info("Connected Wi-Fi，Disable hostapd and dnsmasq")
        return "Connected Successfully", 200
    else:
        logging.error("connect Wi-Fi fail")
        return "Connection Failed", 400

@app.route('/device_info')
def device_info():
    info = get_device_info()
    return jsonify(info)


@app.route('/bluetooth_scan')
def bluetooth_scan_route():
    """
    Route to scan for Bluetooth devices.
    Returns a JSON list of available Bluetooth devices.
    """
    devices = scan_bluetooth()
    return jsonify(devices)

@app.route('/bluetooth_connect', methods=['POST'])
def bluetooth_connect_route():
    """
    Route to connect to a selected Bluetooth device.
    Expects JSON data with 'address' field.
    Returns a success or failure status.
    """
    data = request.json
    address = data.get('address')

    if not address:
        logging.error("No Bluetooth device address provided for connection.")
        return jsonify({"status": "fail", "message": "No Bluetooth device address provided."}), 400

    success = connect_bluetooth(address)
    if success:
        return jsonify({"status": "success", "message": f"Connected to {address}."})
    else:
        return jsonify({"status": "fail", "message": f"Failed to connect to {address}."}), 400


@app.route('/console')
def console():
    return render_template('console.html')

@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.form.get('command')
    # write command to file, the command will be executed by another process in the background (rfcomm)
    with open('command_queue.txt', 'a') as f:
        f.write(command + '\n')
    return 'OK'

@app.route('/get_log')
def get_log():
    try:
        with open('rfcomm_log.txt', 'r') as f:
            log_content = f.read()
        # just return the last 50 lines
        lines = log_content.split('\n')
        last_lines = '\n'.join(lines[-50:])
        return last_lines
    except FileNotFoundError:
        return ''

@app.route('/lcd_control', methods=['POST'])
def lcd_control():
    action = request.form.get('action')
    message = request.form.get('message', '')
    # write command to file, the command will be executed by another process in the background (rfcomm)
    with open('lcd_command.txt', 'w') as f:
        f.write(json.dumps({'action': action, 'message': message}))
    return 'OK'




if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8000)