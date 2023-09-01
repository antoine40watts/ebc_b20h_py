#!/bin/bash

# Check if the script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi


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
udev_rule_file="/lib/udev/rules.d/99-ebc_b20h.rules"

if [[ ! -e "$udev_rule_file" ]]; then
    touch "$udev_rule_file"
    new_line='ACTION=="add", SUBSYSTEMS=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="660", GROUP="plugdev"'
    echo "$new_line" >> "$udev_rule_file"
    echo "File created: $udev_rule_file"
else
    echo "File $udev_rule_file already exist"
fi


echo "Done !"

