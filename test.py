import threading
import random
from time import sleep
from formlayout import fedit
from os import getcwd

import os
import sys
import datetime

def add(a, b):

    sleep(5)
    print(a + b)

class ConfigOptions:
    def __init__(
            self,
            #Experiment Variables
            numTrials=1,
            lickTime=2000,
            itiTime=2000,
            maxIti=3,

            #Stimulus Variables
            leftColor="Green",
            rightColor="Green",
            stimulusTime=100,
            stimulusIntensity=1,

            #Reward Variables
            licks=5,
            rewardSize=1,
            catchRatio=.5,

            #Current Working Directory
            logLocation=getcwd()
    ):
            self.numTrials=numTrials
            self.lickTime=lickTime
            self.itiTime=itiTime
            self.maxIti=maxIti
            self.leftColor=leftColor
            self.rightColor=rightColor
            self.stimulusTime=stimulusTime
            self.stimulusIntensity=stimulusIntensity
            self.licks=licks
            self.rewardSize=rewardSize
            self.catchRatio=catchRatio
            self.logLocation=logLocation

def hello():
    for a in range (0,5):
        print random.randrange(5,11,1)*0.1

class TestClass:
    def __init__(
    self,
    experiment=[1,2],
    stimulus=[3,4]
    ):
        self.item1=experiment[0]
        self.item2=experiment[1]
        self.item3=stimulus[0]
        self.item4=stimulus[1]



if __name__ == "__main__":

    def create_experiment_options(options):
        return [
            ('Number of trials',options.numTrials),
            ('Lick Time (ms)',options.lickTime),
            ('ITI Time (ms)',options.itiTime),
            ('Max Number of ITI',options.maxIti),
        ]

    def create_stimulus_options(options):
        return [
            ('Left Stimulus Color',[options.leftColor,'Green','Blue']),
            ('Right Stimulus Color',[options.rightColor,'Green','Blue']),
            ('Stimulus Duration',options.stimulusTime),
            ('Stimulus Intensity',options.stimulusIntensity),
        ]

    def create_reward_options(options):
        return [
            ('Number of licks for reward',options.licks),
            ('Reward Size (mL)',options.rewardSize),
            ('Reward %',[str(options.catchRatio),'0.00','0.25','0.5','0.75','1.00'])
        ]

    '''
    options = ConfigOptions()
    datalist = create_experiment_options(options)
    datalist2 = create_stimulus_options(options)
    datalist3 = create_reward_options(options)

    new = fedit(((datalist, "Experiment", ""),
                            (datalist2, "Stimulus", ""),
                            (datalist3, "Reward", "")),
                            "Experiment Settings")

    options = ConfigOptions(*new)
    '''

    options = TestClass()
    print options.item2
