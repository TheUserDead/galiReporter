import json
from readsettings import *
import logging
import time
import datetime
import glob
import sys
import subprocess
import gc

if sys.platform == 'linux':
  import fcntl
  import socket
  import struct

import paho.mqtt.client as mqtt
import ftplib
import tarfile
import os
import requests
import globalz

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler("greporter.log"), logging.StreamHandler()])

def restart():
        import sys
        logging.info("argv was",sys.argv)
        logging.info("sys.executable was", sys.executable)
        logging.info("restart now")
        os.execv(sys.executable, ['python3.9'] + sys.argv)

def getHwAddr(ifname):
  if sys.platform == 'linux':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])

def connected_to_internet(url='http://upd.sysspec.ru', timeout=5):
  try:
    _ = requests.head(url, timeout=timeout)
    return True
  except requests.ConnectionError:
    pass
    #logging.info("<!> No internet connection available.")
  except requests.exceptions.ReadTimeout:
    pass
  except urllib3.exceptions.ReadTimeoutError:
    pass
  return False

# def uploads(archfile):
#   logging.info("<i> Upload arch {}".format(archfile))
#   x = settingsRead("server")
#   ftpServer = x[2]
#   ftpUser = x[3]
#   ftpPass = x[4]
#   session = ftplib.FTP(ftpServer,ftpUser,ftpPass)
#   file = open(archfile,'rb') 
#   session.cwd("/")
#   answer = session.storbinary('STOR /{}'.format(archfile[7:]), file)     # send the file and cut start text with foldername
#   answer = answer.split(" ")
#   if answer[0] == "226":
#     logging.info("Upload succesful")
#   file.close()                                    # close file and FTP
#   filelist = glob.glob("upload/*.tar.gz")
#   for n in filelist: # remove all compressed log files
#     os.remove(n)
#   logging.info("Archives Purged")
#   now = datetime.datetime.now()
#   tm = f'{now.year}.{now.month}.{now.day}-{now.hour}:{now.minute}'
#   settingsUpdate("archive", "dateReported", tm)
#   logging.info("Successfull reporting at {}".format(tm))
#   session.quit()

def uploads(): #upload all tar.gz files from upload/ folder
  x = settingsRead("server")
  ftpServer = x[2]
  ftpUser = x[3]
  ftpPass = x[4]
  archlist = glob.glob("upload/*.tar.gz")
  if len(archlist) > 0:
    print(f'Uploading files: {len(archlist)}')
    for i in archlist:
      session = ftplib.FTP(ftpServer,ftpUser,ftpPass)
      file = open(i,'rb') 
      session.cwd("/")
      answer = session.storbinary('STOR /{}'.format(i[7:]), file)     # send the file and cut start text with foldername
      answer = answer.split(" ")
      if answer[0] == "226":
        logging.info(f'Upload succesful {i}')
        os.remove(i) #remove only if uploaded successfully
      else:
        logging.warning('Somethong went wrong while upload {i}, archive not deleted.')
        return False
      file.close()
    now = datetime.datetime.now()
    tm = f'{now.year}.{now.month}.{now.day}-{now.hour}:{now.minute}'
    settingsUpdate("archive", "dateReported", tm)
    logging.info("Successfull reporting at {}".format(tm))
    session.quit()
    return True
  else:
    logging.info('Nothing to upload.')
    return False
  

def updateDrivers(): #update drivers with mqtt!
  with open("drivers.json", "w") as outfile:
      json.dump(response.text, outfile, indent=2)


def check_not_ended_files():
  last_line = ""
  end_marker = 'END'
  logging.info("Archivator")
  filelist = glob.glob("arch/*.log") #create first file list in folder arch
  for n in filelist:
    with open(n, 'r') as f:
      try:
        last_line = f.readlines()[-1]
      except IndexError as e:
        logging.warning(f'Error in make tarfile {e}')
        os.remove(n)
        logging.warning(f'Removed bad file: {n}')
    if last_line.lower().strip() != end_marker.lower():
      logging.info("DEBUG: File {} has not ended!".format(n))
      os.remove(n) #remove not ended files
  filelist[:]
  filelist = glob.glob("arch/*.log")
  if len(filelist) > 0:
    return True
  else:
    logging.info("Nothing to archivate!")
    return False

def make_tarfile(output_filename, source_dir):  #check we have something to archive
  filelist = glob.glob("arch/*.log") #after checking all files
  if len(filelist) > 0:
    with tarfile.open(output_filename, "w:gz") as tar:
      tar.add(source_dir, arcname=os.path.basename(source_dir))
    logging.info(filelist)
    for n in filelist: # remove all uncompressed log files
      os.remove(n)
  else:
    logging.warning('Something wring with data while compress!')

def compress_logs(output_filename, source_dir):  #check we have something to archive
  filelist = glob.glob("*.log") #after checking all files
  if len(filelist) > 0:
    with tarfile.open(output_filename, "w:gz") as tar:
      tar.add(source_dir, arcname=os.path.basename(source_dir))
    logging.info(filelist)
    for n in filelist: # remove all uncompressed log files
      os.remove(n)
  else:
    logging.warning('Something wrong with data while compress!')

def on_message(client, userdata, msg):
  logging.info(msg.topic+" "+str(msg.payload))
  mssg = msg.payload
  topic = msg.topic
  mssg = mssg.decode()
  if topic == "EnvMetrics/CarTrackers/{}/json".format(mqttData[1]):
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    logging.info("data Received type",type(m_decode))
    logging.info("data Received",m_decode)
    logging.info("Converting from Json to Object")
    m_in=json.loads(m_decode) #decode json data
    with open("settings.json", "w") as outfile:
      json.dump(m_in, outfile, indent=2)
      logging.info("Settings Updated!")
  if mssg == "force":
    settingsUpdate("archive", "forceDump", 1)
    logging.info(settingsRead("archive"))
  if mssg == "getconfig":
    try:
      with open('settings.json') as file:
        settingsj = file.read()
      psettj = json.loads(settingsj)
      client.publish("EnvMetrics/CarTrackers/{}/config".format(mqttData[1]), payload=json.dumps(psettj), qos=0, retain=False)
    except FileNotFoundError:
      logging.warning("Settings file not found!")
    

def on_connect(client, userdata, flagc, rc):
  logging.info("Connected with result code "+str(rc))
  logging.info("Connected as client: {}".format(mqttData[1]))
  client.subscribe("EnvMetrics/CarTrackers/{}/#".format(mqttData[1]))
  client.publish("EnvMetrics/CarTrackers/{}/status".format(mqttData[1]), payload="online", qos=0, retain=False)
  client.publish("EnvMetrics/CarTrackers/{}/mac".format(mqttData[1]), payload=macaddr, qos=0, retain=False)

def mqtt_interface(inpt, mess):
  client.publish("EnvMetrics/CarTrackers/{}/{}".format(mqttData[1], inpt), payload=mess, qos=0, retain=False)

def getconfig():
  logging.info("Get current initial configuration for {}".format(macaddr))
  mqttData = [None]*4
  mqttData[0] = "upd.sysspec.ru"  #add yout server and these initial configuration! Remember about ACL!
  mqttData[1] = "configuser"  
  mqttData[2] = "configpass"
  global client;  
  client = mqtt.Client()
  client.on_connect = on_connect_init
  client.on_message = on_message_init
  client.username_pw_set(mqttData[1], password=mqttData[2])
  client.connect_async(mqttData[0], 1884, 60)
  client.loop_start()

def on_message_init(client, userdata, msg):
  mssg = msg.payload
  topic = msg.topic
  mssg = mssg.decode()
  if topic == "EnvMetrics/CarTrackers/config/{}".format(macaddr):
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    logging.info("data Received type",type(m_decode))
    logging.info("data Received",m_decode)
    logging.info("Converting from Json to Object")
    m_in=json.loads(m_decode) #decode json data
    with open("settings.json", "w") as outfile:
      json.dump(m_in, outfile, indent=2)
    #with open('settings.json') as file:
    #  settingsj = file.read()
    #logging.info(settingsj)
    logging.info("<!> Settings Updated! Restart...")
    client.loop_stop()
    restart()

def on_connect_init(client, userdata, flagc, rc):
  client.subscribe("EnvMetrics/CarTrackers/config/{}".format(macaddr))
  client.publish("EnvMetrics/CarTrackers/config", payload=macaddr, qos=0, retain=False)


def main():
  gc.collect()
  global mqttData;
  global macaddr;
  global now;
  if sys.platform == 'linux':
    macaddr = getHwAddr('wlx1cbfceedf93a')
  if sys.platform == 'win32':
    macaddr = '00:BA:DC:0F:FE:EE'
  states = settingsRead("states")
  if states == False:
    getconfig()
  if states != False:
    if connected_to_internet():
      logging.info("Network connected!")
      settingsUpdate("sys", "networkAvailable", 1)
      logging.info("Mac address: {}".format(macaddr))
      try:
        mqttData = [];
        mqttData = settingsRead("mqtt")
        global client
        client = mqtt.Client(client_id="{}".format(mqttData[1]), clean_session=False)
        client.on_connect = on_connect
        client.on_message = on_message
        mqttdata = settingsRead("mqtt")
        client.username_pw_set(mqttData[1], password=mqttData[2])
        # client.connect(mqttData[0], 1884, 60)
        client.connect_async(mqttData[0], 1884, 60)
        client.loop_start()
        client.will_set("EnvMetrics/CarTrackers/{}/status".format(mqttData[1]), payload="offline", qos=0, retain=False)
        if sys.platform == 'linux':
          subprocess.run(["python3", "/home/GaliReporter/reportwifi.py"])
        while connected_to_internet():
          main_two()
      except ConnectionRefusedError:
        logging.warn("Cannot connect to MQTT server!")
      except KeyboardInterrupt:
        client.publish("EnvMetrics/CarTrackers/{}/status".format(mqttData[1]), payload="manual_stop", qos=0, retain=False)
        sys.exit()
      #except Exception as e:
      #  logging.warning(f'<!> error {e}')
      #  logging.info(f'<!> error {e}')
    else:
      print("No network available")
      settingsUpdate("sys", "networkAvailable", 0)

def main_two():
  power = settingsRead("sys")[0]
  if power == 0:
    logging.info("Power lost, ending work")
    sys.exit()
  now = datetime.datetime.now()
  logging.info('Current time is: {}'.format(now))
  filelist = glob.glob("arch/*.log")
  logRepoCounter = len(filelist)
  try:
    uFlag = settingsRead("archive")
  except json.decoder.JSONDecodeError:
    logging.info("<!> Json access parrarel, wait some time...")
    time.sleep(1)
    uFlag = settingsRead("archive") #try again, hope it helps in long delays between reads and writes from two modules
  #except Exception as e:
  #  logging.warning(f'<!> error {e}')
  #  logging.info(f'<!> error {e}')
  if logRepoCounter > 0 and uFlag[7] == 1:
    settingsUpdate("archive", "isUpload", 1)
    logging.info("Arch folder has unreported {} recordings, archivating...".format(logRepoCounter))
    mqtt_interface("status", "Reporting {} records".format(logRepoCounter))
    drv = settingsRead("driver")
    filename = f'upload/{drv[0]}-{now.year}.{now.month}.{now.day}-{now.hour}.{now.minute}.tar.gz'
    if check_not_ended_files():
      make_tarfile(filename, "arch/")
      #compress_logs(filename, "")
    if uploads():
      logging.info(f'Reported on date {filename[7:-7]}')
      settingsUpdate("archive", "uploadFlag", 0)
      settingsUpdate("archive", "isUpload", 0)
    else:
      pass
  time.sleep(30) #just for debug or something

while True:
  try:
    globalz.init_superglobs()
    main()
    time.sleep(60)
  except KeyboardInterrupt:
    logging.info("END")
    sys.exit()
