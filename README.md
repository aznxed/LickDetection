# LickDetection

## Project Overview
Using an Arduino module and voltage sensors, with this application, we will be able to detect mouse licks. 
LEDs act as a stimlus to signal to mice when to begin licking. 
Once the mouse completes the required number of licks for the reward, we enter the intertrial interval(ITI).
If no licks are detected in the ITI, we give the reward. However, if additional licks are detected, we begin another ITI, up to a specified number of max ITIs. 
If that max is exceeded, we proceed to the next trial. 

## Requirements
- This application was built using **Python 2.7** and was not tested on Python3. 
- Standard Firmata must be installed on the Arduino. Learn more about [installing standard firmata](http://www.instructables.com/id/Arduino-Installing-Standard-Firmata/)
- FormLayout. Found [here](https://github.com/PierreRaybaut/formlayout)
- Matplotlib

## GUI


## Threads 
### Main Thread
The main thread deals with Matplotlib and is responsible for live graphing of voltages and events, such as the stimulus or ITI. 

### Lick Thread
The lick thread deals with reading voltages from the Arduino and storing them. When a voltage drop reaches a threshold, we consider it as a lick event. 

### Experiment Thread
The experiment thread deals with the experiment logic, i.e(how many trials to run, intertrial logic).

## Improvement
- Imrpove GUI by adding tabs to make it easier to understand and organize variables
- Remove as many global variables to improve performance 
