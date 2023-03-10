import serial, time, sys



def comm_interface(commandstr):
  #print("<i> Command Interface")
  ser.flush()
  ser.write(commandstr.encode())
  time.sleep(0.1)
  #if ser.in_waiting == 0: ## BUG here while batch_req 
  #  init_comm()
  #if ser.in_waiting > 0:
  ans = ser.read(3)
  if ans.decode() == "0":
    print("<!> ZeroData!")
    return False
  if ans.decode('utf-8') == "IF ":
    ans = ser.read_until(b'\x20') #bytes size heree
    try:
      ssz = int(ans.decode('utf-8')) #convert to right data type
      #print("size = {}".format(ssz)) #report this to console
      ans = ser.read(ssz) # read data stream from serial counted by received size
      #print("<i> Given databank answer: {}".format(ans.hex()))
      return ans
    except ValueError:
      print("Something wrong with packet! Data = {}".format(ans))
      print("Something wrong with packet! Data = {}".format(ans))
      return False
  if ans != "IF":
    while ser.in_waiting > 0:
      ans = ser.read(ser.in_waiting)
    return str(ans)
try:
  ser = serial.Serial('COM12', 19200, bytesize=8, parity='N', timeout=3, rtscts=0, xonxoff=0)
  print("Direct tracker command interface. Uses /dev/ttyACM0 as default")
  print("Use this script to ask/setup tracker for special needs/debug")
  serialcmd = input("Enter command: ")
  x = comm_interface(serialcmd)
  if x != False:
    print(x)
  if x == False:
    print("Something wrong with answer: {}".format(x))
  print("===========================================")
except serial.serialutil.SerialException:
  print("<!> Com port not found! Check connection!")
  sys.exit()