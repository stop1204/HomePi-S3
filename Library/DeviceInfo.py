import socket
import subprocess
import uuid


class DeviceInfo:
    """
    This is a class to facilitate the initialization of some device information for testing

    Class to get information about a device

    for example: IP address, MAC address, hostname, etc.
    """
    _instance = None  # class variable to store the instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DeviceInfo, cls).__new__(cls)
        return cls._instance

    def __init__(self, hostname='Terry.local'):
        """
        Initialize the DeviceInfo class with the given hostname
        :param hostname: default hostname is 'Terry.local'
        """
        if not hasattr(self, '_initialized'):  # prevent reinitialization
            self.hostname = hostname
            self._initialized = True
    def change_hostname(self, hostname):
        """
        Change the hostname of the device
        :param hostname: new hostname or ip address
        :return: None
        """
        self.hostname = hostname

    def ping_host(self):
        try:
            ping_response = subprocess.run(['ping', '-c', '1', self.hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if ping_response.returncode == 0:
                print(f"{self.hostname} is reachable")
                return True
            else:
                print(f"{self.hostname} is not reachable")
                return False
        except Exception as e:
            print(f"Error during ping: {e}")
            return False

    def get_host_ip(self):
        try:
            ip_address = socket.gethostbyname(self.hostname)
            print(f"IP address of {self.hostname}: {ip_address}")
            return ip_address
        except socket.gaierror as e:
            print(f"Error resolving hostname {self.hostname}: {e}")
            return None

    def get_local_ip(self):
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            print(f"Local IP address: {local_ip}")
            return local_ip
        except Exception as e:
            print(f"Error retrieving local IP: {e}")
            return None

    def get_mac_address(self):
        try:
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])
            print(f"MAC Address: {mac_address}")
            return mac_address
        except Exception as e:
            print(f"Error retrieving MAC address: {e}")
            return None

    def get_hostname(self):
        try:
            local_hostname = socket.gethostname()
            print(f"Hostname: {local_hostname}")
            return local_hostname
        except Exception as e:
            print(f"Error retrieving hostname: {e}")
            return None

    def get_network_interfaces(self):
        try:
            # Get network interfaces (this works on macOS)
            # scutil --nwi
            interface_response = subprocess.run(['scutil', '--nwi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            interfaces = interface_response.stdout
            print(interfaces)
            return interfaces
        except Exception as e:
            print(f"Error retrieving network interfaces: {e}")
            return None


device_info = DeviceInfo()
# 獲取全局唯一實例

if __name__ == "__main__":
    device_info.get_host_ip()
    device_info.get_local_ip()
    device_info.get_mac_address()
    device_info.get_hostname()
    device_info.get_network_interfaces()
    ''' results
    Terry.local is reachable
    IP address of Terry.local: 192.168.11.254
    Local IP address: 127.0.0.1
    MAC Address: ff:f5
    Hostname: Terrys-MacBook-Pro.local
    
    Network information
    
    IPv4 network interface information
         en0 : flags      : 0x5 (IPv4,DNS)
               address    : 192.168.11.116
               reach      : 0x00000002 (Reachable)
    
       REACH : flags 0x00000002 (Reachable)
    
    IPv6 network interface information
       No IPv6 states found
    
    
       REACH : flags 0x00000000 (Not Reachable)
    
    Network interfaces: en0
    '''
