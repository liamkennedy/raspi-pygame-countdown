#!/bin/bash
# This script will install the Kano LED Ring Components 
# the microSD card partition on the first boot of a new SD card image

# Enable the scripts
echo "install fonts"
sudo mkdir /usr/share/fonts/truetype/ds_digital
sudo cp ds_digital/* /usr/share/fonts/truetype/ds_digital
sudo mkdir /usr/share/fonts/truetype/coolvetica
sudo cp coolvetica/* /usr/share/fonts/truetype/coolvetica

echo "DONE"
