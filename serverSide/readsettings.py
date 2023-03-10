import json

if __name__ == "__main__":
  print("This file is module for main program 'trackerconnector.py' and cannot be used directly. \nPlease call mentioned file!")

# REWORK TO RETURN DICT!
def settingsRead(type):
  try:
    with open('settings.json') as file:
      settingsj = file.read()
    psettj = json.loads(settingsj)
    if type == "server":
      outlist = [];
      outlist.append(psettj["server"]["addr"])
      outlist.append(psettj["server"]["archUrl"])
      outlist.append(psettj["server"]["ftpServer"])
      outlist.append(psettj["server"]["ftpUser"])
      outlist.append(psettj["server"]["ftpPass"])
      return outlist
    if type == "mqtt":
      outlist = [];
      outlist.append(psettj["mqtt"]["mqttAddr"])
      outlist.append(psettj["mqtt"]["name"])
      outlist.append(psettj["mqtt"]["pass"])
      return outlist
    if type == "driver":
      outlist = [];
      outlist.append(psettj["driver"]["car_num"])
      outlist.append(psettj["driver"]["driverid"])
      return outlist
    if type == "archive":
      outlist = [];
      outlist.append(psettj["archive"]["startDump"])    # 0
      outlist.append(psettj["archive"]["archFile"])     # 1
      outlist.append(psettj["archive"]["placeholder"])  # 2
      outlist.append(psettj["archive"]["dateReported"]) # 3
      outlist.append(psettj["archive"]["packQueue"])    # 4
      outlist.append(psettj["archive"]["profileFile"])  # 5
      outlist.append(psettj["archive"]["timeArchHour"]) # 6
      outlist.append(psettj["archive"]["uploadFlag"])   # 7
      outlist.append(psettj["archive"]["reportingMode"])# 8
      outlist.append(psettj["archive"]["forceDump"])    # 9
      return outlist
    if type == "states":
      outlist = [];
      outlist.append(psettj["states"]["drive"])       #0
      outlist.append(psettj["states"]["mileage"])     #1
      outlist.append(psettj["states"]["wheelCounter"])#2
      outlist.append(psettj["states"]["timeUpdated"]) #3
      return outlist
    if type == "initial":
      outlist = [];
      outlist.append(psettj["initial"]["configured"])
      outlist.append(psettj["initial"]["initialCommands"])
      return outlist
  except FileNotFoundError:
    print("<!> Settings file not found! Need request confdata!")
    #By default it can get settings init file from server.
    #But i'm lazy and want to made initial MQTT connection with default user and send MAC as ClientID.
    #If mac registered - server generates and response initial configuration
    return False #by return false, reporter program try to get initial confiiguration. We don't need add mqtt handling here.
  except KeyError:
    print("<!> Something wrong with JSON keys, config is UP to DATE?")
  except TypeError:
    print("<!> Something wrong with JSON keys, config is UP to DATE?")

def settingsUpdate(what, who, data):
  try:
    with open('settings.json') as file:
      settingsj = file.read()
    psettj = json.loads(settingsj)
    print("<i> readsettings.update: {} {} {}".format(what, who, data))
    if what == "archive":
      archsub = psettj["archive"]
      if who == "startDump":
        archsub["startDump"] = data
      if who == "archFile":
        archsub["archFile"] = data
      if who == "placeholder":
        archsub["placeholder"] = data
      if who == "dateReported":
        archsub["dateReported"] = data
      if who == "packQueue":
        archsub["packQueue"] = data
      if who == "timeArchHour":
        archsub["timeArchHour"] = data
      if who == "uploadFlag":
        archsub["uploadFlag"] = data
      if who == "forceDump":
        archsub["forceDump"] = data
      psettj["archive"] = archsub
    if what == "initial":
      initsub = psettj["initial"]
      if who == "configured":
        initsub["configured"] = data
      if who == "initialCommands":
        initsub["initialCommands"] = data
      psettj["initial"]= initsub
    if what == "states":
      statessub = psettj["states"]
      if who == "drive":
        statessub["drive"] = data
      if who == "mileage":
        statessub["mileage"] = data
      if who == "wheelCounter":
        statessub["wheelCounter"] = data
      psettj["states"] = statessub
    with open("settings.json", "w") as outfile:
      json.dump(psettj, outfile, indent=2)
  finally:
    pass
