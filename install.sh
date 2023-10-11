#!/bin/bash

# Check if the script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi


# Changing hostname
hostnamectl set-hostname battest


# Add the lines to the /etc/network/interfaces file
echo "Adding CAN interface to /etc/network/interfaces"

new_lines="auto can0
iface can0 can static
    bitrate 250000"

interfaces_file="/etc/network/interfaces"

if ! grep -qF "$new_lines" "$interfaces_file"; then
    echo "$new_lines" >> "$interfaces_file"
    echo "Lines added successfully to $interfaces_file"
else
    echo "Lines are already present in $interfaces_file"
fi


# Adding a rule to acces a USB device
echo "Adding a UDEV rule to acces EBC-B20H over USB"
udev_rule_file="/lib/udev/rules.d/99-battest.rules"

if [[ ! -e "$udev_rule_file" ]]; then
    touch "$udev_rule_file"
    new_line='ACTION=="add", SUBSYSTEMS=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="660", GROUP="plugdev"'
    echo "$new_line" >> "$udev_rule_file"
    echo "File created: $udev_rule_file"
else
    echo "File $udev_rule_file already exist"
fi


# Installing required packages and modules
echo "Installing required packages and modules"
apt install git can-utils python3-pip -y


# Installing nodejs
echo "Installing NodeJs"
if [[ ! -e "/etc/apt/sources.list.d/nodesource.list" ]]; then
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
    NODE_MAJOR=20
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
    sudo apt-get update
fi
sudo apt-get install nodejs -y


# Installing npm modules
echo "Installing npm modules"
cd front
npm install
cd ..

# Installing required Python modules
echo "Installing required Python modules"
pip install -r requirements


# Setting up the web server autostart at boot time
echo "Setting up the web server autostart"

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Name of the service (adjust as needed)
SERVICE_NAME="battest"

# Path to the bash script
SCRIPT_PATH="$SCRIPT_DIR/run.sh"

# Create the systemd service file
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

if [[ ! -e "$SERVICE_FILE" ]]; then
cat > "$SERVICE_FILE" <<EOL
[Unit]
Description=Battery Testing Software

[Service]
Type=simple
ExecStart=$SCRIPT_PATH
WorkingDirectory=$SCRIPT_DIR
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Make the service file readable only by root
chmod 644 "$SERVICE_FILE"
else
    echo "$SERVICE_FILE already exists"
fi

# Enable and start the service
systemctl enable "$SERVICE_NAME.service"
systemctl start "$SERVICE_NAME.service"

# Check the service status
systemctl status "$SERVICE_NAME.service"

echo "End of installation script"
echo "You should reboot the system with 'sudo reboot'"