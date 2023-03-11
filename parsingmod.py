import glob
import requests
import logging
import sys
import globalz
from datetime import datetime
from readsettings import *
#clotch with time definition bcz network unavailable most of time
global datasizes, datanames, datatypes, carnum, now, imei, driver
seletedschemafle = 0;
datasizes = [];
datanames = [];
datatypes = [];
timeByteOrder = None

if __name__ == "__main__":
  print("This file is module for main program 'trackerconnector.py' and cannot be used directly. \nPlease call mentioned file!")

def file_attach(hard, soft):
  if hard == False or soft == False:
    return False
  print("<i> File attach")
  global now, carnum, imei, driver
  now = datetime.now()
  carnum = settingsRead("driver")[0]
  driver = settingsRead("driver")[1]
  archSet = settingsRead("archive")


  if archSet[5] == "none": # this works when file not setup, we need check hw+sw to found near digits file. Example HW is 11 but SW is 229. We have 230, use this version. 11-230.json 
    try:                   # algoritm not best, it's just looks near digit from list but two digits can be from two different files! But it works! (Sometimes not, running on OPi i96 works different!)
      filelist = glob.glob("profiles/*.json") #get all json files on directory
      print(filelist)
      files = [word[9:-5] for word in filelist] # magically get only filenames 
      filesss = [word.split('-') for word in files]
      l = []
      for sublist in filesss:
        for item in sublist:
          l.append(int(item))
      nearfilefwver = l[min(range(len(l)), key=lambda i: abs(l[i]- soft))] # find near digits of sv
      global seletedschemafle
      seletedschemafle = f'{hard}-{nearfilefwver}.json' # here we assemble full fle name
      print(f'Selected file: {seletedschemafle}')
      settingsUpdate("archive", "profileFile", seletedschemafle)
    except FileNotFoundError as err:
      print("<!> JSON SChema not found!")
      logging.critical("<!> JSON SChema not found!")
      sys.exit()
  
  if archSet[5] != "none": # if autoselection not works, use manual json schema file selection. just write just name of file on settings.json
      seletedschemafle = archSet[5]
      print(f'Schema file from settings file: {seletedschemafle}')
  
  try:
    with open('profiles/{}'.format(seletedschemafle)) as file:
      dataj = file.read()
    parsedj = json.loads(dataj)
    itemsize = len(parsedj["archive"]["item"]) # size of tags in json schema   
  #Get data from schema, sizes\names\types
    global datasizes;
    for n in range(22):
      datasizes.append(int(parsedj["archive"]["item"][n]["_size"]))
  # get names of each data
    global datanames;
    for n in range(22):
      datanames.append(parsedj["archive"]["item"][n]["_name"])
    #print(datanames)
    global datatypes;
    for n in range(22):
      datatypes.append(parsedj["archive"]["item"][n]["_format"])
    globalz.timeByteOrder = parsedj["archive"]["time_byte_order"]
  except FileNotFoundError as err:
    print("<!> Configured JSON SChema not found!")
    logging.critical("<!> Configured JSON SChema not found!")
    sys.exit()


def parser(dataz, filenm, clss):
  # print("<i> Parser")
  #parse data with JSON loaded schema
  pointerjson = 0
  datax = [];
  datas = [];
  bytebuff = bytearray()
  for n in range(22):
    try:
      datax.append(dataz[pointerjson:][:datasizes[n]].hex())
      pointerjson = pointerjson + datasizes[n]
    except AttributeError:
      print("<!> Something wrong when decode data: {}".format(dataz[pointerjson:][:datasizes[n]]))
      logging.warning("<!> Something wrong when decode data: {}".format(dataz[pointerjson:][:datasizes[n]]))
  #print("------UNCONVERTED DATA!----------")
  #for n in range(22): 
  #  out = "dataname: {} data: {}".format(datanames[n], datax[n])
  #  print(out)
  #define some vars before read convert type and pre-handle data using data type
  for n in range(22):
    if datatypes[n] == "uint" or datatypes[n] == "int" or datatypes[n] == "sat":
      if datasizes[n] > 1: #no need byte swapping if data size just one byte
        bytebuff = bytearray.fromhex(datax[n])
        bytebuff.reverse() #-------------
        if datatypes[n] == "uint":
          datax[n] = int.from_bytes(bytebuff, "big", signed=False)
        if datatypes[n] == "int": #note: LAT & LON has int type
          datax[n] = int.from_bytes(bytebuff, "big", signed=True)
          # verify coordinates!
          if datanames[n] == "LAT" or datanames[n] == "LON":
            datax[n] = datax[n]/1000000
            if verify_gps(datax[n]):
              pass
            else:
              datax[n] = 0.000001
              print(f'<!> Wrong data detected!: {datax[n]}')
        if datanames[n] == "SPD":
          ### TRACCAR uses knots as default speed system, GALLILEO uses km\h speed display without comma.
          ### add key in settings to miles\sec and convert km\h to mps\sec here!
          ### ADD to /conf/traccar.xml <entry key='osmand.speed'>mps</entry> and see true data in traccar!
          datax[n] = (datax[n] / 10) / 3.6
          datax[n] = round(datax[n], 2)
      if datasizes[n] == 1:
        datax[n] = int(datax[n], 16) 
    if datatypes[n] == "string":
      if datanames[n] == "IMEI":
        # No need IMEI for easy car id registration and driver id verify Just replace with driver id, but imei stored in confoguration and log file header.
        #bytebuff = bytearray.fromhex(datax[n])
        #datax[n] = bytebuff.decode()
        datax[n] = f'{carnum}'; #here we don't use IMEI as car ID, master device is PC.
      if datasizes[n] >= 20:
        datax[n] = 'none'
    if datatypes[n] == "dt": 
      bytebuff = bytearray.fromhex(datax[n])
      if globalz.timeByteOrder == "LE":
        buff = int.from_bytes(bytebuff, "little", signed=False)
      if globalz.timeByteOrder == "BE":
        buff = int.from_bytes(bytebuff, "big", signed=False)
      datax[n] = buff 
      
#############################
  # print("-----------PARSED DATA!------------")
  # for n in range(22): 
  #   out = "dataname: {} data: {}".format(datanames[n], datax[n])
  #   print(out)
     #print(datetime.utcfromtimestamp(datax[5]).strftime('%Y-%m-%d %H:%M:%S'))
   #datout = "{}".format(datax)
   #print(datax)
  if filenm != 'None':
    file_dump(datax, filenm, clss)
  if filenm == 'None':
    return datax

def file_dump(datain, filenm, clss):
  # report_ext(datain[2], datain[8], datain[9], datain[6], datain[13], datain[11], datain[10])
  ### NOT checking file exists for failsafe, think about it!
  with open(filenm, 'a') as f: #####BUG HERE!!! rechckek
    #print('{}'.format(datain), file=f)
    f.write("{}\n".format(datain))
    if clss == True: 
      f.write("{}\n".format(datanames))
      f.write("END") # by this mark file counted as ended. For cases when data not readed completely!
      f.close()
      print("<i> Succesful archived")

def report_ext(ids, lat, lon, time, hdop, alt, speed, driver):
  print(speed)
  serverurl = settingsRead("server")[1] #not use at this time! bad when re-read every time when stream mode launches!
  x = requests.get(f'{serverurl}id={ids}&lat={lat}&lon={lon}&timestamp={time}&hdop={hdop}&altitude={alt}&speed={speed}&driverUniqueId={driver}')
  if x == "<Response [200]>":
    pass
  if x == "<Response [400]>":
    print("<!> Error when send GET reuest!")

def verify_gps(value):
    if -90.000000 <= value <= 90.000000 and value == value:
        return True
    return False
