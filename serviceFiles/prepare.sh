#!/bin/sh
INTFS="wlan0"
echo "---Add cron job for autostart---" 
#crontab -l > mycron #if need keep current cron, but fail if cron already empty
#touch mycron
#######echo "@reboot cd /home/GaliReporter && sh prestart.sh" >> mycron
# check wifi interface is available
#####TESTWLAN = ifconfig wlan0 | awk '/^eth0:/ {print $1}'
######echo $TESTWLAN
#if statement!!!!!!!!!
#echo "setup WIFI"
#ip link set dev $INTFS up
#systemctl stop NetworkManager
#systemctl disable NetworkManager-wait-online NetworkManager-dispatcher NetworkManager
#echo "What is your network name?"
#read SSID
#echo "What is your network PASSWORD?"
#read SSPASSWD
#echo "------------------------------------------------------------------------------------"
#echo "Later you can add more networks with:"
#echo "wpa_passphrase SSID SSPASSWD | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf"
#echo "Or just use addwifi.sh"
#echo "------------------------------------------------------------------------------------"
#echo "add wifiscript"
#touch /home/GaliReporter/serviceFiles/addwifi.sh
#echo "echo \"Wifiname:\"" >> /home/GaliReporter/serviceFiles/addwifi.sh
#echo "read SSID" >> /home/GaliReporter/serviceFiles/addwifi.sh
#echo "echo \"wifi passwd:\"" >> /home/GaliReporter/serviceFiles/addwifi.sh
#echo "read SSPASSWD" >> addwifi.sh
#echo "wpa_passphrase \$SSID \$SSPASSWD | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf" >> /home/GaliReporter/serviceFiles/addwifi.sh
#echo "add wpasupplicant.conf"
#touch /etc/wpa_supplicant/wpa_supplicant.conf
#echo "ap_scan=1" >> /etc/wpa_supplicant/wpa_supplicant.conf
#echo "autoscan=periodic:10" >> /etc/wpa_supplicant/wpa_supplicant.conf
#echo "disable_scan_offload=1" >> /etc/wpa_supplicant/wpa_supplicant.conf
#echo "register network"
#wpa_passphrase $SSID $SSPASSWD | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf
#wpa_supplicant -B -c /etc/wpa_supplicant/wpa_supplicant.conf -i $INTFS
#dhclient $INTFS
#echo "working with services"
#cp /home/GaliReporter/serviceFiles/wpa_supplicant.service /etc/systemd/system/wpa_supplicant.service
#systemctl daemon-reload
#systemctl enable wpa_supplicant.service
#cp /home/GaliReporter/serviceFiles/dhclient.service /etc/systemd/system/dhclient.service
#systemctl enable dhclient.service
###crontab mycron
###rm mycron
#nmcli dev set $INTFS managed no
cp /home/GaliReporter/serviceFiles/armbian-default.yaml /etc/netplan/armbian-default.yaml
#netplan apply armbian-config.yaml
echo "add tmuxinator project"
mkdir /root/.tmuxinator
cp /home/GaliReporter/serviceFiles/tconnector.yml /root/.tmuxinator/tconnector.yml
echo "add logrotate settings"
cp /home/GaliReporter/serviceFiles/galireporter /etc/logrotate.d/galireporter
echo "---Done!---"
