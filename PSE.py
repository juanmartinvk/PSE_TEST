# -*- coding: utf-8 -*-
import pygame.mixer as mixer
#import time
import sys
import random
from PyQt5.uic import loadUi
#from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QFileDialog, QListWidgetItem, QErrorMessage


ref_filename = "STIMULI/ref.wav"
#stimuli = ["STIMULI/63HZ -23LUFS -6dB.wav", "STIMULI/125HZ -23LUFS +6dB.wav"]

def dbToLin(num):
    x = 10**(num/20)
    return x

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
    
    
        # self.Next=TestWindow(self.testNumber+1)
        # self.Next.show()
        # self.close()
    
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