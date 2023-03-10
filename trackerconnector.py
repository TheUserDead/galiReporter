#TODO insys parse for batt voltage

import logging
import sys
import time
import datetime
import os.path

from requester import *        #module what do ther stuff like requesting data\states\init
from parsingmod import *       #module for parce receivef drom device data
from readsettings import *     #module for reading\writing settings.json
import globalz                 #global variables module
version = "0.8"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler("gconnector.log"), logging.StreamHandler()])

start_time = time.time()

def init():
  #possible logic bug! When car is preparing to go, device can reboots some times! Like when starter working. Need filter this like after 1m startup.
  # -- satisfied by filter in reporter module. When log reads to compress, every file checks END section to know file is ended or no. That's means all data received and cleared from device.
  try:
    globalz.init_superglobs()
    # globalz.main()
    print(f'Stating version: {version}')
    settingsUpdate("archive", "forceDump", 1) #by this every boot device reads data from tracker. 
    settingsUpdate("sys", "powerPresent", 1) #update flag because device start
    settingsUpdate("archive", "isDump", 0) #update flag because device start
    #globalz.isDump = 0
    serialconn()
  except serial.serialutil.SerialException as err:
    logging.critical("<!> Com port not found! Check connection!")
  #except:
    #  logging.warning(f'<!> error {e}')
    #  logging.info(f'<!> error {e}')

def powerEnd():
  power = settingsRead("sys")[0]
  if power == 0:
    logging.info("Power lost, ending work")
    logging.warning("--- %s seconds ---" % (time.time() - start_time))
    sys.exit()

def main():
  while True:
    try:
      comreq = check_comm();
      if comreq == False:
        init_comm()
      if comreq:
        get_status(0) # 0 - is default
        if settingsRead("sys")[1] == 0:
          print('No network available, get time from GPS')
          get_status(1) # updtate time 
        if settingsRead("sys")[1] == 1:
          print('Network available, timefrom NTP!')
        globalz.now = datetime.now()
      reslt = settingsRead("archive")
      logging.info(reslt)
      reslt2 = settingsRead("driver")
      states = settingsRead("states")
      if reslt[8] == "uploadDump":
         # CHANGE on on_load_get has only bootup reporting! Flags doesn't track \ update in time!
        if reslt[9] == 1 and reslt[4] >= 4: # checking forca flag and available records. It's must be not less than 50
          logging.info("<i> Start archivating...")
          settingsUpdate("archive", "uploadFlag", 0) ## update flag we have and ready to report data to server
          settingsUpdate("archive", "forceDump", 0)
          settingsUpdate("archive", "isDump", 1) ## update flag we at progess
          #globalz.isDump = 1
          filename = ("arch/{}-{}.{}.{}-{}.{}.log".format(reslt2[0], globalz.now.year, globalz.now.month, globalz.now.day, globalz.now.hour, globalz.now.minute)) ###rework filename, it's can change!
          logging.info(filename)
          with open(filename, 'w') as f:
            f.write(f'Recs:{reslt[4]}:Wheels:{states[2]}:Mileage:{states[1]}:IMEI:{globalz.imei} \n') #Write info about day summary. Wheel counter, GPS mileage and records count.
          batch_req(reslt[4], filename) # rework with globalz
          settingsUpdate("archive", "uploadFlag", 1) ## update flag we have and ready to report data to server
          settingsUpdate("archive", "isDump", 0) ## update flag we end read progress
          #globalz.isDump = 0
          # logging.info("<i> Data ready for startDump changed to 1") #startDump deprecated?
        elif reslt[9] == 1 and reslt[4] < 4:
          settingsUpdate("archive", "forceDump", 0) #we don't want make only 500 records file!
      if reslt[8] == "streamDump": #for future implement streamin reporting while network available
        logging.info("<!> Currently not implemented code! Do nothing, successfully :)") 
      time.sleep(30)
      powerEnd()
    except serial.serialutil.SerialException as err:
      logging.critical("<!> Com port not found! Check connection! \n Repeat in 3 sec...")
      time.sleep(3)
      serialconn()
    except KeyboardInterrupt:
      logging.info("--- %s seconds ---" % (time.time() - start_time))
      sys.exit()
    #except:
    #  logging.warning(f'<!> error {e}')
    #  logging.info(f'<!> error {e}')

  
init()
main()

#AVAILABLE DATATYPES
# uint\int - integer little endian possible the same just byte size 8x 16x 32x 64x etc.
# string - just string big endian
# dt - datetime unixtime
# lat\lon
#hw 11 - v1.8.5 lite
#hw 17 - v2.3.5
#hw 19 - v5.0.0
#hw 130 - 7.0 lite
#hwclock --set --date="2013-7-31 09:30"