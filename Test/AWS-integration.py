





# pip install boto3
# $:aws configure
# default region: ap-east-1

'''
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install cmake
sudo apt-get install libssl-dev

sudo apt-get install git

sudo apt install python3

sudo apt install python3-pip

# cd ~
# python3 -m pip install awsiotsdk
# git clone https://github.com/aws/aws-iot-device-sdk-python-v2.git


'''

'''
sudo apt update && sudo apt upgrade -y

sudo reboot

sudo apt install git -y

sudo apt install pip -y

git clone https://github.com/aws/aws-cli.git

cd aws-cli

git switch v2

sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old

pip install -r requirements.txt

pip install .

sudo reboot

aws --version

aws configure --profile profileName

...
    
aws s3 ls

sudo locale-gen en_HK.UTF-8
sudo dpkg-reconfigure locales
export LANG=en_HK.UTF-8
export LC_ALL=en_HK.UTF-8

# install VLC
sudo apt-get install --reinstall vlc
sudo apt-get install vlc-plugin-* libvlc* libvlccore*
sudo chmod -R 755 /usr/lib/vlc
pip install python-vlc --break-system-packages
find /usr -type d -name 'plugins' -path '*/vlc/*' 2>/dev/null
ls /usr/lib/aarch64-linux-gnu/vlc/plugins
ls /usr/include/vlc/plugins
export VLC_PLUGIN_PATH=/usr/lib/aarch64-linux-gnu/vlc/plugins
export VLC_PLUGIN_PATH=/usr/include/vlc/plugins
echo 'export VLC_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/vlc/plugins' >> ~/.bashrc
source ~/.bashrc
sudo chmod -R 755 VLC_PLUGIN_PATH=/usr/lib/aarch64-linux-gnu/vlc/plugins
sudo chmod -R 755 VLC_PLUGIN_PATH=/usr/include/vlc/plugins


'''

'''
VLC issue: cannot run VLC in ssh. must run in local terminal or remote desktop
'''