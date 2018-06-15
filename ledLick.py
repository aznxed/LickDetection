import pickle
import random
import threading
import matplotlib
import psutil, os, sys
import logging
import serial.tools.list_ports

matplotlib.use('qt4agg')
matplotlib.rcParams['backend.qt4'] = "PySide"
import matplotlib.animation as anim
import matplotlib.pyplot as plt

from Tkinter import Tk
from os import getcwd
from sys import exit
from time import clock, sleep
from time import strftime
from tkFileDialog import asksaveasfilename
from flexx import ui
from formlayout import fedit
from pyfirmata import Arduino, util

CONFIGLOCATION = "./LEDLick.config"
DEBUG = False

p = psutil.Process(os.getpid())
p.nice(psutil.HIGH_PRIORITY_CLASS)

class ConfigOptions:
    def __init__(
            self,
            color="Blue",
            numTrials=1,
            licks=5,
            reward=1,
            lickTime=2000,
            lightTime=100,
            catchRatio=.5,
            itiTime=2000,
            maxIti=3,
            logLocation=getcwd()
    ):
            self.color = color
            self.numTrials = numTrials
            self.licks = licks
            self.reward = reward
            self.lightTime = lightTime
            self.lickTime = lickTime
            self.catchRatio = catchRatio
            self.itiTime = itiTime
            self.maxIti = maxIti
            self.logLocation = logLocation


def wait(lengthMS):
    s = clock()
    while (clock() - s) * 1000 < lengthMS:
        pass

def setThresh():
	global lickSense
	mean = 0.0
	while lickSense.read() is None:
		continue
	for i in range(1000):
		ls = lickSense.read()
		mean += ls/1000.0
	return mean*.95


def setUpMenu():

    Tk().withdraw()

    try:
    	with open(CONFIGLOCATION,"r") as f:
    		options = pickle.load(f)
    except (IOError, EOFError, pickle.PickleError):
    	options = ConfigOptions()

    menuData = [
    	('Color',[options.color,'Green','Blue']),
    	('Number of trials',options.numTrials),
    	('Number of licks for reward',options.licks),
    	('Reward Size (mL)',options.reward),
    	('Lick Time (ms)',options.lickTime),
    	('Stimulus Length (ms)',options.lightTime),
    	('Reward %',[str(options.catchRatio),'0.00','0.25','0.5','0.75','1.00']),
        ('Intertrial Interval Time',options.itiTime),
        ('Max Number of ITI', options.maxIti)
    ]

    newData = fedit(menuData,title="LED Stimulus Options")
    if newData is None:
    	exit()

    path = asksaveasfilename(initialdir="\\".join(options.logLocation.split('\\')[:-1]),title="Save log as...",defaultextension = ".log",initialfile="\\LEDLick"+strftime("%Y-%m-%d_%H.%M.%S")+".log")
    if path is not '':
    	newData.append(path)

    options = ConfigOptions(*newData)
    with open(CONFIGLOCATION,"w+") as f:
    	pickle.dump(options,f)

    return options


def setUpLogger(options):
    logger = logging.getLogger('LEDStim')
    return logger


def setUpArduino(options):
    global rLED
    global lLED
    global lickSense
    global rewardPin

    ports = list(serial.tools.list_ports.comports())
    connectedDevice = None
    for p in ports:
    	if 'Arduino' in p[1]:
    		try:
    			connectedDevice = Arduino(p[0])
    			print ("Connected to" + str(connectedDevice))
    			break
    		except serial.SerialException:
    			print ("Arduino detected but unable to connect to " + p[0])
    if connectedDevice is None:
    	exit("Failed to connect to Arduino")

    board = connectedDevice
    lickSense = board.get_pin("a:0:i")
    greenLEDRight = board.get_pin("d:5:p")
    blueLEDRight = board.get_pin("d:6:p")
    greenLEDLeft = board.get_pin("d:9:p")
    blueLEDLeft = board.get_pin("d:10:p")
    rewardPin = board.get_pin("d:8:o")
    it = util.Iterator(board)
    it.daemon = True
    it.start()
    lickSense.enable_reporting()

    rLED = greenLEDRight
    lLED = greenLEDLeft
    if options.color == "Blue":
    	rLED = blueLEDRight
    	lLED = blueLEDLeft

    return connectedDevice, rLED, lLED


def logData(data, file):
    global startTime
    global options
    global plt

    t = clock()-startTime
    dl = str(t)+"s: "+data+'\n'
    with open(file,'a') as fp:
        fp.write(dl)
    if "Catch" in data:
		plt.axvspan(t,t+float(options.lickTime)/1000.0+float(options.lightTime)/1000.0, facecolor='#FFCCCC', alpha=.25)
    elif "Reward" in data:
        plt.axvspan(t,t+float(options.lickTime)/1000.0+float(options.lightTime)/1000.0, facecolor='#CCFFCC', alpha=.25)
    elif "Giving reward" in data:
        plt.axvspan(t,t+options.reward, facecolor='c', ymax=.75, alpha=.5)
    elif "Lick detected" in data:
        plt.axvspan(t,t+.1, facecolor='g', ymax=.5, alpha=.5)
    elif "Stimulus on" in data:
        plt.axvspan(t,t+float(options.lightTime)/1000.0, facecolor='#FFFF00', ymax=.75, alpha=.5)
    elif "Intertrial" in data:
        plt.axvspan(t,t+options.reward, facecolor='b', ymax=.75, alpha=.5)


def stimulus(rLED, lLED, logFile, options, intensity=1):
	logData("Stimulus on with intensity "+str(intensity),logFile)
	rLED.write(intensity)
	lLED.write(intensity)
	wait(options.lightTime)
	rLED.write(0)
	lLED.write(0)
	logData("Stimulus off",logFile)


def waitForLicks(options):
    global sensing
    sensing = True
    wait(options.lickTime)
    sensing = False

def waitForLicksITI(options):
    global sensing
    sensing = True
    wait(options.itiTime)
    sensing = False

def lick(logFile):
    global licks
    global sensing
    logData("Lick detected",logFile)
    print("Lick Detected")

    if sensing:
        licks += 1

def giveReward():
	global options
	global rewardPin
	global logFile
	logData("Giving reward",logFile)
	rewardPin.write(1)
	wait(options.reward*1000)
	rewardPin.write(0)


def runExp(options, logFile):
    global startTime
    global lickThreadRun
    global licks
    global rLED
    global lLED
    global interTrial

    startTime = clock()
    for trial in range(options.numTrials):
        sleep(1)

        if random.random() > float(options.catchRatio):
            reward = False
            logData("(Catch) Start Trial " +str(trial),logFile)
        else:
            reward = True
            logData("(Reward) Start Trial " +str(trial),logFile)

        print("Start Trial")
        licks = 0
        stimulus(rLED, lLED, logFile, options)
        waitForLicks(options)

        if reward:
            if licks >= options.licks:
                giveReward()
                interTrial(options)

        logData("End Trial " +str(trial),logFile)
        print("End Trial")
    lickThreadRun = False


def writeLick(data, options):
	if len(data) != 2:
		return
	with open(options.logLocation[:-4]+".lick.log", 'a') as fp:
		fp.write(str(data[0])+','+str(data[1])+'\n')


def lickDetect(options):
    global lickSense
    global lickData
    global lickThreadRun
    global startTime
    global logFile

    new = lickSense.read()
    old = lickSense.read()

    while lickThreadRun:
        sleep(.01)
        t = clock()
        new = lickSense.read()
        if new is not None and old is not None and startTime >= 0:
            writeLick([t-startTime,new], options)
            lickData[0].append(t-startTime)
            lickData[1].append(new)
            if old-new > .2:
                lick(logFile)
        old = new

def interTrial(options):
    global licks
    global logFile
    additionalLick = True
    numITI = 0
    maxIti = options.maxIti

    while(additionalLick and numITI < maxIti):
        numITI = numITI + 1
        logData("Intertrial " +str(numITI),logFile)
        print("Enter ITI " + str(numITI))
        newLick = licks
        waitForLicksITI(options)
        oldLick = licks

        if(newLick == oldLick):
            additionalLick = False
            print("No additional licks")
            break
        print("Additional Lick detected")

    if(numITI == maxIti):
        print("Max ITI reached")


logger = logging.getLogger('LEDStim')
def logHandle(type, val, tb):
	logger.exception("Uncaught exception: {0}".format(str(value)))
sys.excepthook = logHandle


def main():
    global startTime
    global rLED
    global lLED
    global sensing
    global rewardPin
    global lickSense
    global lickThreadRun
    global lickData
    global options
    global logFile

    startTime = -1
    options = setUpMenu()
    logger = setUpLogger(options)
    board = setUpArduino(options)

    sensing = True
    logFile = options.logLocation
    licks = 0
    sensing = False
    lickThreadRun = True
    lickData = [[],[]]
    lickBuffer = []
    threshold = setThresh()

    lickThread = threading.Thread(target=lickDetect, args=(options,))
    lickThread.start()

    expThread = threading.Thread(target=runExp, args=(options, logFile))
    expThread.start()

    pageWidth = options.lickTime/500
    fig = plt.figure(frameon=False)
    sub = fig.add_subplot(1,1,1)
    ax = plt.gca()
    ax.set_ylim([threshold-.2,threshold+.05])
    ax.set_xlim([-10,10])
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    line, = sub.plot(lickData[0],lickData[1])
    plt.show(block=False)
    plt.pause(0.001)

    while lickThreadRun and plt.fignum_exists(fig.number):
    	ld = [[],[]]
    	ld[0] = lickData[0][:]
    	ld[1] = lickData[1][:]
    	m = min(len(ld[0]),len(ld[1]))
    	if m is 0:
    		continue
    	line.set_xdata(ld[0][:m])
    	line.set_ydata(ld[1][:m])
    	lastTime = float(ld[0][-1])
    	ax.set_xlim([lastTime-10,lastTime+5])

    	ax.redraw_in_frame()
    	fig.canvas.update()
    	fig.canvas.flush_events()

    if plt.fignum_exists(fig.number):
    	plt.show(block=True)


main()
