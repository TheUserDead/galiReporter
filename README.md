# GaliReporter
If you need offline car tracker data receiving without cellular internet, you can use this repo to do this.
Based on any Orange Pi computer and Python3.6+ it's dumps all data from tracker in end of day and report to server when configured wifi is available.
Using Traccar software as tracks management & view and OSMAnd protocol to upload data.

Currently working functions:  
 - [x] Time fix GPS\Network time selection. Currently only gps in compete with automatic NTP update  
 - [x] recognize our tracker number for keep the same car number (bug when replace&reconfigure)  
 - [x] recognize tracker for profile configuration preset (no more re-read tracker version)  
 - [x] automatic handling little-endian and big-endian when decode data form tracker  
 - [ ] server creating initial configuration per device  
 - [ ] server mqtt handler for initial configuration sender  
 - [ ] registering new mqtt client\traccar\ftp\db_record
 - [ ] known list of devices (config ecosys)  
 - [x] traccar local parser  
 - [x] db for mileage data from trackers by day summary (leaved as is, focused to use traccar functions with own counting)
 - [ ] GPS-Based mileage counting on DB 
 - [x] replace device IMEI to device internal ID 
 - [x] logging debug information  
 - [x] GPS-Based milage recording handling (client)  
 - [x] manual setup profiler file.  
 - [x] deploying on clear systems script  
 - [x] configuring initial system for work scripts and services  
 - [x] daemon-like running with tmux session (cause i want monitor script at this time)  
 - [x] connect to usb-serial device in three different addresses and reconnect every 3 secs if connect unsuccessful  
 - [x] parsing gallileosky trackers with autoselect profile file (first digits hw-vesion, second firmware digits of sw)  
 - [x] Dump tracker data when boot device (car engine started) and more than 50 records available  
 - [x] Check archived tracks has end of read. Uncomplete files just ignore and remove. For short-time booting situations.  
 - [x] Reporting compressed tracks via FTP  
 - [x] Send informational data via MQTT while network is available  
 - [x] Request force read from device and get archive  
 - [x] Initial configuration per device, setup ports mode, filters, etc   
 - [x] report current configuration  
 - [x] update current configuration  
 - [x] connect to initial server and get configuration from it  
 - [x] upload and streaming mode tracks reporting. Currently only upload mode (stream needs more time for network connection, but directly sends data to tracker server. For any choice.)  

This project has 3 modules:  
1 - trackerconnector.py: handle usb-serial communication with gallileosky device and tracking states.  
    Input data  
    GPS time (+ timezone offset) and update system time, because OrangePi cannot have RTC and internet to know current time.  
    Records counter  
    GPS based mileage (currently no implemented. Added ASAP)  

2 - reporter.py: monitoring network available  
    Compess one-day dumped data and upload this when internet available using FTP.  
    Purge old data automatically on trackerand SBC
    MQTT state\command interface   

3 - powercontroller.py > controller.py (later): monitor power of SBC, module working supervisor. 
    When power on PC7 port goes to GND system will shutdown for 1 min.
    Later this script mainenance system statuses, updates and modules working

Software structured as daemon-like system. Not true daemon. Just TMuxinator project on user root folder. 

Logic of "trackerconnector":  
  When started it's try initialize communication with /dev/ttyACM (0/1/2) devices.  
  It's try every 3 seconds to reconnect serial.  
  After init conmmunication it's request HW and SW of tracker to select profile file automatically.  
  Every 5 min device state (can be reconfigured) and gets time from GPS to setup time on device.  
  From 00:00 to 09:00 when device bootup, it reads archive from device to /arch folder via .log file and send command to tracker for clean internal memory.  
  from 09:00 to 19:00 device set 'upload' flag what means data is ready send to server when network is available.  
  Between status checks it's track force reading function, update system time,  

Logic of "reporter":  
  Looks fot network available (before this you must precinfigure wifi network and autoscan&connect)  
  If network available, it's check arch/ folder with .log files and compress it with tar.gz, flush .log files, connect to ftp and upload archive. And of course, cleanup archive from the device. Between this module reports onlin state, report records and can update\report it's own config and receive commands from serverlike force archive read and upload.  

settings.json description  
Note: Only used data is described. Other keys will be removed in future bacause i resolve tasks\logic and something changes, optimizing, clothing.  
-- Archive:  
     - uploadFlag:(bool) marks data is ready for upload. managed by "trackerconnector" for "reporter" module and set to 1 after receive all tracker data.  
     - startDump:(bool) flag 1 - means trackerconnector can retrieve all data from tracker based on "pack" number, but not less 50 records  
     - forceDump:(bool) managed from reporter module. When force command received it's changed and trackerconnector forcefully start read all available data  
     - dateReported:(timedate) time last reported data to server. Creates when archive uploaded.  
     - profileFile:(filename) forcefully setup profiler file for parser. Sometimes python or running machine CAN counr abs function incorrectly! --Not implemented at this time.  
     - packQueue:(num) Number of records reported by tracker. By this number batch read data cont on this.  
     - reportingMode:(text uploadDump / streamDump) upload mode for tracker. Upload is fast but needs external parser to traccar.  
     Stream send data directly to traccar server using http API. Takes some time! --not implemented at this time.  
-- Initial:
     - configured:(bool) flat for understand, device need to be configured to use in this system or not. If 0 it's parse next key and executes it. Last command is set device number!  
     - initialCommands:(text with | delimiter) custom commands for setup tracker by operator needs like GPS filters, ports mode and edges.  
-- driver:
     - driverid:(num) for future here's stores current driver who drice the car  
     - car_num:(num) like car-id defines current car and replaced in future by mqtt user  
-- server:
     - ftpServer:(address) ftp server address  
     - ftpUser:(text) user from frp server  
     - ftpPass:(text) password from ftp server  
     - archUrl:(address) stream mode URL  
     - addr:(address) i forgot what is for :(  
-- mqtt:
     - mqttAddr:(address) address of ftp server  
     - user:(text) mqtt username and the same clientid  
     - pass:(text) mqtt user password  
-- states:
     - mileage:(num in meters) current GPS counted by tracker tracker mileage. Not reseting.  
     - wheelCounter:(num in cycles) for future, possible wheel counter connected and reported here. it's analog for milage. --not tested\implemented  
     - drive(bool) signal for tracker if car is ignited. Possible removed in future because logic is changed  

***IMPORTANT NOTIFY ABOUT WIFI AND NETWORKING***
  This code is referenced to use debian 9 OrangePi example. Uses wireless interface like wlan0.  
  You need replace with yours in prepare.sh  
  Currently some devices has unstable working (as i think) OrangePi i96, OrangePi 3G-IOT-B has some problems while setup and connect.  
  This need adapt for your OS and hardware! Currently i use netplan as best solution for wifi connection and OrangePi pc plus/one/zero2 as host machine.
  Wifi adapter buildin or based on rtl5370 as great wifi module 