# this is module for listening mqtt messages from trackers and generated answer to configure devices.

import json
import time
import subprocess
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))
  mssg = msg.payload
  topic = msg.topic
  mssg = mssg.decode()
  if topic == "EnvMetrics/CarTrackers/config":
    print("<i> Someone wants configure: {}".format(mssg))
    mac = mssg.split(":")
    if len(mac) != 6:
      print("<!> Wrong MAC addr!")
    if len(mac) == 6:
      with open('current.txt', 'r+') as f:
        linee = f.readline()
        linee = int(linee)
        print("<i> Line: {}".format(linee))
      with open('users.txt', 'r') as f:
        lines = [line.rstrip() for line in f]
      user = lines[linee]
      passw = generate_temp_password(10)
      print("<i> REG.mqtt {} {}".format(user, passw))
      result = subprocess.run(["mosquitto_passwd", "-b", "/etc/mosquitto/conf.d/hs.pwd", user, passw], capture_output=True)
      print(result.stdout)


def generate_temp_password(length):
    if not isinstance(length, int) or length < 8:
        raise ValueError("temp password must have positive length")

    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    from os import urandom

    # original Python 2 (urandom returns str)
    # return "".join(chars[ord(c) % len(chars)] for c in urandom(length))

    # Python 3 (urandom returns bytes)
    return "".join(chars[c % len(chars)] for c in urandom(length))
    

def on_connect(client, userdata, flagc, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("EnvMetrics/CarTrackers/config/#".format(mqttData[1]))

def init():
  try:
    global mqttData;
    mqttData = ['127.0.0.1','configurator','configpass'];
    global client
    client = mqtt.Client(client_id="{}".format(mqttData[1]), clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(mqttData[1], password=mqttData[2])
    client.connect_async(mqttData[0], 1884, 60)
    client.loop_start()
  except ConnectionRefusedError:
    print("Cannot connect to MQTT server!")

def main():
  pass

init()
while True:
  time.sleep(3)
  main()