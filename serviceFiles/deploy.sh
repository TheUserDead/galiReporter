#!/bin/bash
#Need Python 3.8+
INTFS="wlan0"
echo "================================================================"
echo "---This script installs all need environment for this project---"
echo "================================================================"
apt install python3 -y
apt install python3-pip -y
apt install python3-dev -y
apt install tmux -y
apt install tmuxinator -y
apt install locales -y
echo "LC_ALL=en_US.UTF-8" >> /etc/environment
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf
locale-gen en_US.UTF-8

pip3 install --upgrade pip 
pip3 install pyserial
pip3 install requests
pip3 install paho-mqtt
cp /home/GaliReporter/serviceFiles/upd.sh /home/upd.sh
echo "---Add cron job for autostart---"
crontab -l > mycron #if need keep current cron, but fail if cron already empty
echo "@reboot tmuxinator start tconnector" >> mycron
crontab mycron
rm mycron
cp /home/GaliReporter/serviceFiles/armbian-default.yaml /etc/netplan/armbian-default.yaml
echo "add tmuxinator project"
mkdir /root/.tmuxinator
cp /home/GaliReporter/serviceFiles/tconnector.yml /root/.tmuxinator/tconnector.yml
echo "add logrotate settings"
cp /home/GaliReporter/serviceFiles/galireporter /etc/logrotate.d/galireporter
echo "================================================================"
echo "    Completed! \nRead README for understand what is all for.    "
echo "================================================================"