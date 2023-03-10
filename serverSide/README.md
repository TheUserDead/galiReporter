Server side module for manage known devices and add new
Project roadmap:
- support argument commands
  - add new device
  - remove device
  - manual configuration update (pending mode)
- damon script for listening mqtt for requests (device interact layer with API)
  - extract mac address and check device is known 
  - register device on system
  - create account in mqtt
  - create account in traccar
  - create account in ftp
  - gnerate json configuration and send it back
  - listening device status info and add logs to mysql: online\offline\reporting\mileage\driverid\etc
  - based on peding updates, update device config if it changes on server.

MYSQL table planning
database: trackers
  table: devices
    |______deviceID_____|_____deviceMAC______|______mqttUser_______|_____mqttPass_____|______configured______|
             num                 MAC                   text               text                boolean
  
  table: datas
    |_____deviceID____|_____timestamp_____|___driverID___|____mileage____|_____status_____|_____lastSeen____|
             num               datetime          num            num            text             datetime