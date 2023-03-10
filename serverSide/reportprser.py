import tarfile
import glob
import requests
from readsettings import *
import time
import os
import sys
import subprocess

global serverurl, crutch

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

def unpack():
  filelist = glob.glob("cartracker/*.tar.gz")
  if len(filelist) != 0:
    print(f'<i> Current archives is {len(filelist)}')
    for n in filelist:
      file = tarfile.open(n)
      file.extractall('unpacked/')
      file.close()
    for i in filelist:
      os.remove(i)
  else:
    print('No track reports available')
    sys.exit()

def report_req(ids, lat, lon, times, hdop, alt, speed, pack, driver):
  print(pack)
  serverurl = settingsRead("server")[1]
  x = requests.get(f'{serverurl}id={ids}&lat={lat}&lon={lon}&timestamp={times}&hdop={hdop}&altitude={alt}&speed={speed}&driverUniqueId={driver}')
  time.sleep(0.05)
  if x == "<Response [200]>":
    print("s")
  if x == "<Response [400]>":
    print("<!> Error when send GET reuest!")

def batch_handler():
  loglist = glob.glob("unpacked/*.log")
  print(f'<i> Current archives is {len(loglist)}')
  for i in loglist:
    print(f'Parse {i}')
    with open(i) as fl:
      for line in progressbar(fl, "Upload:", 40):
        parser(line)
  #################################COPY DATA BUG
  for i in loglist:
    os.remove(i)
  print('===Completed===')

def parser(dat):
  global crutch
  try:
    dt = dat.split(",")
    dt = [x.strip(' ') for x in dt]
    dt = [x.strip("'") for x in dt]
    print(f'Device={dt[2]}, lat={dt[8]}, lon={dt[9]}, time={dt[6]}, hdop={dt[13]}, alt={dt[12]}, speed={dt[10]}, driver={dt[4]}')
    if dt[0] == "END":
      pass
    if dt[6] == 'TMD':
      pass
    bytebuff = bytearray()
    if dt[6] != 'TMD':
      ################################### Temporary crutch e.g. dirty hack from old software dumps!
      if len(dt[6]) < 9:
        print(type(dt[6]))
        dt[6] = crutch
        dt[6] = int(dt[6])+5
      # ########################################### CUT THIS CRUTCH BY THIS LINE
      report_req(dt[2], dt[8], dt[9], dt[6], dt[13], dt[12], dt[10], dt[5], dt[4])
      crutch = dt[6]######## this line remove too!
  except IndexError:
    pass

def main():
  unpack()
  batch_handler()

main()


