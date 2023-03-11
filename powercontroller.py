from pyA20.gpio import gpio
from pyA20.gpio import port
from pyA20.gpio import connector
import time
import subprocess
import sys
from readsettings import *

gpio.init()
sns = port.PC7
gpio.setcfg(sns, gpio.INPUT)

print("Starting watching power at PC7")
while True:
  pw = gpio.input(sns)
  if pw == 1:
    #print("Power lost: init safe shutdown")
    settingsUpdate("sys", "powerPresent", 0) #flag says power lost, if currently dump\upload is active, program reads this status after end of reading\uploading
    isdump = settingsRead("archive")[0]
    isupload = settingsRead("archive")[1]
    while isdump: #if yes just pass do nothing 
      time.sleep(10)
      isdump = settingsRead("archive")[0]
    while isupload: #if yes just pass do nothing 
      time.sleep(10)
      isdump = settingsRead("archive")[1]
    if not isdump: #if reading active - not shutdown
      subprocess.call(['shutdown'])
      sys.exit()
    if not isupload: #id not uploading - not shutdown
      subprocess.call(['shutdown'])
      sys.exit()
  time.sleep(30)
