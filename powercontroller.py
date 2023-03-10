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
    while settingsRead("archive")[0] == 1: #if yes just pass do nothing 
      time.sleep(10)
    if settingsRead("archive")[0] == 0: #if no just shutdown
      subprocess.call(['shutdown'])
      sys.exit()
  time.sleep(30)