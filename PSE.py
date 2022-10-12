# -*- coding: utf-8 -*-
import pygame.mixer as mixer
#import time
import sys
import os
import csv
# import numpy as np
import random
from PyQt5.uic import loadUi
#from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QFileDialog, QListWidgetItem, QErrorMessage


ref_filename = "STIMULI/ref.wav"


class Stimulus():
    def __init__(self):
        self.boostFrequency=0
        self.offset=0
        self.userCorrection=0
        self.filename=""
        

class TestWindow(QMainWindow):
    def __init__(self, stimuli):
        super(TestWindow, self).__init__()
        
        # Load designed UI
        loadUi("./GUI/pse_gui.ui",self)
        mixer.init()
        
        self.stimuli=stimuli
        self.testNumber = 1
        self.stimIndex=0
        self.csvPath=""
        
        self.offset = self.stimuli[self.stimIndex].offset
        self.initVolume = -18
        self.ref = mixer.Sound(ref_filename)
        self.ref.set_volume(dbToLin(self.initVolume))
        self.stim = mixer.Sound(self.stimuli[self.stimIndex].filename)
        self.stim.set_volume(dbToLin(self.initVolume + self.offset))
        self.testNumLabel.setText("Test "+str(self.testNumber)+"/"+str(len(stimuli)))
        
        
        #Button bindings
        self.playButton1.clicked.connect(self.playRef)
        self.playButton2.clicked.connect(self.playStim)
        self.stopButton.clicked.connect(self.stopPlayback)
        self.volumeControl.valueChanged.connect(self.setVolume)
        self.nextButton.clicked.connect(self.nextTest)
        self.plusVolume.clicked.connect(self.raiseVolume)
        self.minusVolume.clicked.connect(self.lowerVolume)

    def playRef(self):
        mixer.stop()
        self.ref.play()
        
    def playStim(self): 
        mixer.stop()
        self.stim.play()
        
    def stopPlayback(self):
        mixer.stop()
        
    def setVolume(self):
        volume = dbToLin(self.volumeControl.value() / 10 + self.initVolume + self.offset)
        #print(self.volumeControl.value() / 10)
        #print(self.stim.get_volume())
        self.stim.set_volume(volume)
    
    def raiseVolume(self):
        increment = 2
        vc = self.volumeControl.value()
        if vc <= 120:
            self.volumeControl.setValue(vc + increment)
        else:
            self.volumeControl.setValue(120)
        self.setVolume()
        
    def lowerVolume(self):
        increment = -2
        vc = self.volumeControl.value()
        if vc >= -120:
            self.volumeControl.setValue(vc + increment)
        else:
            self.volumeControl.setValue(-120)
        self.setVolume()
    
    def nextTest(self):
        mixer.stop()
        self.stimuli[self.stimIndex].userCorrection = self.volumeControl.value()/10
        
        if self.testNumber == len(self.stimuli):
            self.exportData()
            self.close()
        else:
            self.stimIndex += 1
            self.testNumber += 1
            self.offset = self.stimuli[self.stimIndex].offset
            self.stim = mixer.Sound(self.stimuli[self.stimIndex].filename)
            self.stim.set_volume(dbToLin(self.initVolume + self.offset))
            self.volumeControl.setValue(0)
            self.testNumLabel.setText("Test "+str(self.testNumber)+"/"+str(len(self.stimuli)))
            
    def exportData(self):
        file_types = "CSV (*.csv)"
        default_name = "data.csv"
        options = QFileDialog.Options()
        # Save File dialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Save as... File', default_name, filter=file_types, options=options)
        
        f=["f [Hz]"]
        offset=["Offset [dB]"]
        uc=["User correction [dB]"]
        diff=["Difference [dB]"]
        for stim in self.stimuli:
            f.append(stim.boostFrequency)
            offset.append(stim.offset)
            uc.append(stim.userCorrection)
            diff.append(stim.offset + stim.userCorrection)
            
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([f, offset, uc, diff])

            
def dbToLin(num):
    x = 10**(num/20)
    return x

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


stimuli = []
frequencies = [63, 125, 4000, 8000]
offsets = [6, 4, -4, -6]
for f in frequencies:
    for offset in offsets:
        stim = Stimulus()
        stim.boostFrequency = f
        stim.offset = offset
        stim.filename="STIMULI/"+str(f)+".wav"
        stimuli.append(stim)

random.shuffle(stimuli)




        
# main
app = QApplication(sys.argv)

test = TestWindow(stimuli)
test.show()



try:
    sys.exit(app.exec_())
except:
    mixer.stop()
    print("Exiting")