#import Tkinter as tk
import os
import sys
from time import clock
from time import sleep
import threading
import psutil

import serial.tools.list_ports
from Tkinter import Button, Frame, Tk
from pyfirmata import Arduino, util


p = psutil.Process(os.getpid())
p.nice(psutil.HIGH_PRIORITY_CLASS)

class GUIButtons:
    def __init__(self, master, rLED, lLED, lickPin, rewardPin):
        frame = Frame(master)
        frame.pack()
        bottomFrame = Frame(master)
        bottomFrame.pack()

        self.leftLED = Button(frame, text="Left LED", command=lambda: testButton(1))
        self.leftLED.pack(side="left", pady=5, padx=5)

        self.rightLED = Button(frame, text="Right LED", command=lambda: testButton(2))
        self.rightLED.pack(pady=5, padx=5)

        self.solenoid = Button(bottomFrame, text="Solenoid", command=lambda: testButton(3))
        self.solenoid.pack(pady=5, padx=5)

        self.lickSensor = Button(bottomFrame, text="Lick Sensor", command=lambda: testButton(4))
        self.lickSensor.pack(pady=5, padx=5)

def wait(lengthMS):
    s = clock()
    while (clock() - s) * 1000 < lengthMS:
		pass

def testButton(number):
    global lickThreadRun

    if number == 1:
        print "Testing left LED"
        lLED.write(1)
        wait(1000)
        lLED.write(0)
    elif number == 2:
        print "Testing right LED"
        rLED.write(1)
        wait(1000)
        rLED.write(0)
    elif number == 3:
        print "Testing reward pin"
        rewardPin.write(1)
        wait(1000)
        rewardPin.write(0)
    elif number == 4:
        print "Testing lick sensor"
        lickThreadRun = True
        lickThread = threading.Thread(target=lickDetect)
        lickThread.start()
        wait(2000)
        lickThreadRun = False
        lickThread.join()

def setUpArduino():
    global rLED
    global lLED
    global lickPin
    global rewardPin
    global it
    global board

    ports = list(serial.tools.list_ports.comports())
    connectedDevice = None
    for p in ports:
    	if 'Arduino' in p[1]:
    		try:
    			connectedDevice = Arduino(p[0])
    			print "Connected to" + str(connectedDevice)
    			break
    		except serial.SerialException:
    			print "Arduino detected but unable to connect to " + p[0]
    if connectedDevice is None:
    	exit("Failed to connect to Arduino")

    board = connectedDevice
    lickPin = board.get_pin("a:0:i")
    greenLEDRight = board.get_pin("d:5:p")
    blueLEDRight = board.get_pin("d:6:p")
    greenLEDLeft = board.get_pin("d:9:p")
    blueLEDLeft = board.get_pin("d:10:p")
    rewardPin = board.get_pin("d:8:o")
    it = util.Iterator(board)
    it.daemon = True
    it.start()
    lickPin.enable_reporting()

    rLED = greenLEDRight
    lLED = greenLEDLeft


def lickDetect():
    global lickPin
    global lickThreadRun

    new = lickPin.read()
    old = lickPin.read()
    print "Begin lick detection"
    while lickThreadRun:
        sleep(.01)
        t = clock()
        new = lickPin.read()
        if new is not None and old is not None:
            if old-new > .2:
                print "Lick detected"
        old = new
    print "End lick detection"

def main():
    global rLED
    global lLED
    global lickPin
    global rewardPin
    global board
    global lickThreadRun

    setUpArduino()

    root = Tk()
    root.geometry("300x200")
    GUIbuttons = GUIButtons(root, rLED, lLED, lickPin, rewardPin)
    root.mainloop()
    board.exit()


main()
