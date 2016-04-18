from __future__ import division
import sys
sys.path.append("..")


import fileinput
import re
import math
import random
import time

from task_mixin import *

from sequencer.sequencer_base import Sequencer
from trial import Trial

class TaskHeadfix(TaskMixin):
    """A stimless task used during headfix acclimation"""

    def __init__(self, training, shrewDriver):
        self.training = training
        self.shrewDriver = shrewDriver
        self.makeStuff()
        
    def prepareTrial(self):
        pass
    
    def makeTrialSet(self):
        pass
        
    def start(self):
        self.changeState(States.REWARD)
    
    def checkStateProgression(self):
        now = time.time()
        
        if self.state == States.TIMEOUT:
            timeSinceLick = now - self.lastLickAt
            timeSinceStateStart = now - self.stateStartTime
            if timeSinceStateStart > self.rewardCooldown and not self.isLicking and timeSinceLick > self.rewardCooldown:
                #Shrew hasn't licked for a while, so make reward available
                self.changeState(States.REWARD)
               
        if self.state == States.REWARD:
            #Wait for the shrew to stop licking
            if self.lastLickAt > self.stateStartTime and self.lastLickAt != 0:
                self.training.dispense_reward(self.rewardBolus / 1000)
                self.changeState(States.TIMEOUT)
                
    def changeState(self, newState):
        #runs every time a state changes
        #self.training.log_plot_and_analyze("State" + str(self.state), time.time())
        self.stateStartTime = time.time()
        self.state = newState
        
        #if changed to timeout, reset trial params for the new trial
        if (newState == States.TIMEOUT):
            #tell UI about the trial that just finished
            print "Got bolus: " + str(self.rewardBolus) + " mL at " + str(time.time()) + "\n"
            #self.shrewDriver.sigTrialEnd.emit()
        
        print 'state changed to ' + str(States.whatis(newState))
    
    def checkFailOrAbort(self):
        pass
    
    def fail(self):
        pass

    def abort(self):
        pass
    
    def prepareGratingState(self): 
        pass
    
    def setUpCommands(self):
        #overwrite parent
        pass
        
    def makeTrialSet(self):
        #overwrite parent
        pass


    #--- Interactive UI commands ---#
    def ui_start_trial(self):
        if self.state == States.TIMEOUT or self.state == States.INIT:
            self.training.log_plot_and_analyze("User started trial")
            print "User started trial"
            self.change_state(States.REWARD)

    def ui_dispense(self, rewardMicroliters):
        timestamp = time.time()
        self.training.syringeSerial.write(str(int(rewardMicroliters)) + "\n")
        self.training.log_plot_and_analyze("user_reward:" + str(rewardMicroliters), timestamp)
        print "User gave reward: " + str(int(rewardMicroliters))
        self.training.send_stimcode(STIMCODE_REWARD_GIVEN)

    def ui_fail_task(self):
        self.training.log_plot_and_analyze("Trial failed at user's request")
        print "Trial failed at user's request"
        self.fail()

