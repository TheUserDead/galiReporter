import serial
import time
import pickle
import os
import sys
from datetime import datetime, timedelta
import logging

from readsettings import *
from parsingmod import *
import globalz

#for access object anywhere
global ser, carmove, soft, hard, currentserial, timeclotch, badread
currentserial = 0
timeclotch = 2023
badread = 0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler("grequester.log"), logging.StreamHandler()])

if __name__ == "__main__":
  print("This file is module for main program 'trackerconnector.py' and cannot be used directly. \nPlease call mentioned file!")

def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.3+
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

def check_comm():
  #logging.info("<i> Check comm")
  serialcmd = "XYZ 0"
  ser.write(serialcmd.encode())
  time.sleep(0.5)
  #logging.info("Waiting data: {}".format(ser.in_waiting))
  if ser.in_waiting > 0:
    s = ser.read(ser.in_waiting)
    # if s == (b'XYZ OK\x00'):
    if len(s.decode()) > 4:
      ser.flush()
      time.sleep(0.5)
      return True
  else:
    return False

def serialconn():
  global currentserial;
  #logging.info("<i> Serr connn")
  notInitializedPort = True;
  while notInitializedPort:
    try:
      # global currentserial;
      global ser;
      if sys.platform == 'linux':
        seri = f'/dev/ttyACM{currentserial}'
      if sys.platform == 'win32':
        seri = f'COM12'
      ser = serial.Serial(seri, 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
      logging.info("<i> Succesful use {} port".format(seri))
      comreq = check_comm();
      if comreq == False:
        init_comm()
      while file_attach(req_ver("h"), req_ver("s")) == False:
        logging.error("Something wrong with read version! Retry")
        time.sleep(5)
        continue
      logging.info("Detected version: {}-{}".format(req_ver("h"), req_ver("s")))
      notInitializedPort = False
      initial_devconf()
    except serial.serialutil.SerialException as err:
      #logging.critical("<!> Com port not found! Check connection!")
      logging.info("Com port not found! Check connection! Use {} port".format(seri))
      time.sleep(5)
      logging.info("Try use different serial...")
      currentserial += 1
      if currentserial > 2:
        currentserial = 0



def req_ver(type):
  #logging.info("<i> Request version")
  if type == "h":
    hhw = comm_interface("hardversion").split("=")
    try:
      hardware = hhw[1].split(",")[0]
    except IndexError as e:
      logging.error(f' occured {e}')
      return False
    #ha = ha.split(",")
    #hardware = ha[0]
    # global hard
    hard = int(hardware)
    logging.info(hard)
    return hard
  if type == "s":
    ssv = comm_interface("status").split("=")
    try:
      software = ssv[1].split(".")[0]
    except IndexError as e:
      logging.error(f' occured {e}')
      return False
    #sv = sv.split(".")
    #software = sv[0]
    # global soft
    soft = int(software)
    logging.info(soft)
    return soft

def init_comm():
  logging.info("Init com port")
  global notInitializedPort;
  notInitializedPort = True;
  while notInitializedPort:
    if ser.in_waiting > 0:
      ser.flush()
    serialcmd = "<CMD REGIME 192837465>"
    ser.write(serialcmd.encode())
    time.sleep(1)
    s = ser.read(25)        # read up to ten bytes (timeout)
    logging.info(s)
    while len(s.decode()) == 0:
      logging.info("Cannot get answer, repeating request with predicted answer...")
      time.sleep(5)
      ser.write(serialcmd.encode())
      time.sleep(1)
      s = ser.read(25)
      logging.info(s)
    serialcmd = "XYZ ttt"
    ser.write(serialcmd.encode())
    time.sleep(1)
    s = ser.read_until(b'\x00')
    logging.info(s)
    if s == (b'XYZ OK\x00'):
      serialcmd = "XYZ 0"
      ser.write(serialcmd.encode())
      time.sleep(1)
      s = ser.read(10)
      if s == (b'XYZ OK\x00'):
        logging.info(s)
        notInitializedPort = False
        logging.info("<Com init complete. Not Initialized: {}".format(notInitializedPort)) #bad logic with false flag
        ser.flush()
      else:
        logging.warn("Cannot init com port!")
        sys.exit()

def initial_devconf():
  x = settingsRead("initial")
  cimei = get_status(2)
  if x[0] == cimei:
    logging.info("It's our configured device :)")
    globalz.imei = cimei
  # assign driver id here! Later here system checks NFC card!----------------------!
  # every time when driver wants to move, they need authorize by NFC itd command ID x used to identify driver on tracks. 
  # Tracker can store ID and device identifien by IMEI what we replace by config.
    driver = settingsRead("driver")[1]
    comm_interface(f'ID {driver}')
    logging.info(f'Driver ID is: {driver}')
  #--------------------------
  if x[0] != cimei:
    if len(x[0]) > 10:
      logging.warning(f'Device changed! from {x[0]} to {cimei} reconfigure')
    else:
      logging.info(f'New Device: {cimei} set default paramaters: \n - Device ID and commands from settings.json')
    initcomms = x[1]
    initcomms = initcomms.split("|")
    for a in initcomms:
      logging.info(comm_interface(f'{a}'))
      time.sleep(1)
    settingsUpdate("initial", "devSerial", cimei)
    settingsUpdate("archive", "profileFile", "none") #RESET schema file if replaced tracker device. It's cause problem when read if it's different version!
  
def keep_link():   # This soubrotine working sort of "keep alive" logic. COM port can be disabled by device sometimes.
  serialcmd = "<CMD REGIME 192837465>"
  ser.write(serialcmd.encode())
  time.sleep(1)
  s = ser.read_until(b'\x00')
  # s = ser.read(22)
  logging.info(s)

def batch_req(end, filenm):
  logging.info(f'Batch request from 1 to {end}')
  cls = False
  end = int(end) + 1
  endi = range(1, end)
  global badread
  for i in progressbar(endi, "Received: ", 40):
    x = "IF {}".format(i)
    s = comm_interface(x)
    clss = False
    if i == end - 1: 
      clss = True
      logging.info(comm_interface("erasetrack")) #clear internal storage
      logging.info(comm_interface("setmileage 0")) #set mileage to 0
    if s != False:
      parser(s, filenm, clss) #???????? connected?
    if s == False and i > 100:
      settingsUpdate("archive", "isDump", 0) # move for other time report cause this time tracker purged his data but not update records counter
      logging.warning(f'Current read has problem. Bug in data cell counting by device. Req: {i}')
    if s == False:
      settingsUpdate("archive", "isDump", 0) # move for other time report cause this time tracker purged his data but not update records counter
      logging.warning("Read has no data. Possible bug.")
      badread +=1
    if s == False and badread > 2:
      badread = 0
      logging.warning("Read cancelled!")
      return


def comm_interface(commandstr):
  #logging.info("<i> Command Interface")
  ser.flush()
  ser.write(commandstr.encode())
  time.sleep(0.1)
  ans = ser.read(3)
  if ans.decode() == "0":
    logging.warning("ZeroData!")
    return False
  if ans.decode('utf-8') == "IF ":
    ans = ser.read_until(b'\x20') #bytes size heree
    #print(f'Debug: Answer says size {ans}')
    if ans == b'1\x00':
      print('EXCEPT')
      logging.warning(f'No data to read, this is a bug! {ans}')
      return False
    try:
      ssz = int(ans.decode('utf-8')) #convert to right data type
      #logging.info("size = {}".format(ssz)) #report this to console
      ans = ser.read(ssz) # read data stream from serial counted by received size
      #logging.info("<i> Given databank answer: {}".format(ans.hex()))
      return ans
    except ValueError:
      logging.warning("Something wrong with packet! Data = {}".format(ans))
      return False
  if ans != "IF":
    while ser.in_waiting > 0:
      ans = ser.read(ser.in_waiting)
    return str(ans)

def get_status(type):
# default update status
  if type == 0:
    parseStatus(comm_interface("status"), 1)
    time.sleep(0.5)
    parseStatus(comm_interface("inall"), 2)
    time.sleep(0.5)
    parseStatus(comm_interface("statall"), 3)
# update time using gps
  if type == 1: 
    parseStatus(comm_interface("status"), 0)
    time.sleep(0.5)
    keep_link()
  if type == 2:
    x = parseStatus(comm_interface("imei"), 4)
    return x

def parseStatus(data, type):
  if type == 0:
    x = data.split(" ")
    time = x[3][5:]
    date = x[4]
    timeee = datetime.strptime('{} {}'.format(date, time), '%d.%m.%y %H:%M:%S')
    timeee = timeee + timedelta(hours=3) #>>> !!! OUR TIMEZONE !!!
    # logging.info(pack, time, timeconv)
    if timeee.year == timeclotch:
      print(os.system(f'date --set="{timeee}"'))
    elif timeee.year != timeclotch:
      logging.warning("Wrong time based on GPS")
  if type == 1:
    x = data.split(" ")
    pack = x[2][5:]
    pack = int(pack)
    settingsUpdate("archive", "packQueue", pack)
  if type == 2: # read sensor like engine status
    x = data.split(",")
    #zero_in = x[0][10:]
    one_in = x[1][4:]
    carMove = one_in
    #settingsUpdate("states", "wheelCounter", zero_in)
    settingsUpdate("states", "drive", one_in)
  if type == 3: # read mileage
    x = data.split(",")
    mileage = x[3]
    mileage = mileage[mileage.find("=")+1:]
    mileage = mileage[0:mileage.find(";")]
    settingsUpdate("states", "mileage", mileage)
  if type == 4: #read device IMEI
    imei = data.split(" ")[1][:15]
    return imei
    