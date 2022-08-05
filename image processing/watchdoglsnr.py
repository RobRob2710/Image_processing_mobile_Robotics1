#!/usr/bin/python3

#imports
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from networktables import NetworkTables
from networktables.util import ntproperty
import threading
import os

#Create the barcodes file
f = open('/home/pi/image processing/array_data.txt', 'w')
f.close()

#Create thread to make sure networktables is connected
cond = threading.Condition()
notified = [False]

#Create a listener
def connectionListener(connected, info):
    with cond:
        notified[0] = True
        cond.notify()

#Instantiate NetworkTables
NetworkTables.initialize(server="10.12.34.2")
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

#Wait until connected
with cond:
    if not notified[0]:
        cond.wait()

#Create the vision Table

ntWorkorderData = ntproperty('/Vision/workorderData', "null")
ntReadWorkorder = ntproperty('/Vision/readWorkorder', False)

#Get Table
table = NetworkTables.getTable('Vision')

#Create the system handler
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        try:
            file = open('./home/pi/image processing/array_data.txt', 'r')
            table.putString('barcodeData', file.readline())
            file.close()
        except:
            pass #when file is not created yet

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='./home/pi/image processing/array_data.txt', recursive=False)
observer.start()

#The forever loop
while(True):
    if table.getBoolean('readWorkorder', False) == True:
        table.putBoolean('readworkorder', False)
        os.system('python3 /home/pi/image processing/readWorkorder.py')
    try:
        pass
    except KeyboardInterrupt:
        observer.stop()
