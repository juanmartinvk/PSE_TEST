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
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

#QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


ref_filename = resource_path("STIMULI/ref.wav")

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
        loadUi(resource_path("./GUI/pse_gui.ui"),self)
        mixer.init()
        
        self.setWindowTitle("Test de percepción subjetiva")
        
        self.stimuli=stimuli
        self.testNumber = 1
        self.stimIndex=0
        self.csvPath=""
        self.started = False
        self.finished=False
        
        self.offset = self.stimuli[self.stimIndex].offset
        self.initVolume = -18
        self.ref = mixer.Sound(ref_filename)
        self.ref.set_volume(dbToLin(self.initVolume))
        self.stim = mixer.Sound(self.stimuli[self.stimIndex].filename)
        self.stim.set_volume(dbToLin(self.initVolume + self.offset))
        
        
        
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
        
        if self.started == False:
            self.started = True
            self.testNumLabel.setText("Test "+str(self.testNumber)+"/"+str(len(stimuli)))
            self.nextButton.setText("Siguiente")
            self.labelVolume.setText("Volumen")
            self.labelNext.setText("Una vez que sientas que los audios están sonando al mismo volumen, hacé click en Siguiente para pasar a la próxima comparación.")
            self.labelAudio2.setText("Ajustá el volumen de este audio para que suene al mismo nivel que el Audio 1.")
            self.labelAudio1.setText("Escuchá este audio todas las veces que quieras, y compará su volumen con el del Audio 2. No es necesario que lo escuches siempre completo.")
            self.audioBox2.setEnabled(True)
            self.volumeControl.setEnabled(True)
            self.plusVolume.setEnabled(True)
            self.minusVolume.setEnabled(True)
            self.audioBox2.setTitle("Audio 2")
        
        elif self.finished == True:
            self.exportData()
            self.close()
        
        else:
            self.stimuli[self.stimIndex].userCorrection = self.volumeControl.value()/10

            if self.testNumber == len(self.stimuli):
                self.finished = True
                self.nextButton.setText("Exportar")
                self.playButton1.setEnabled(False)
                self.playButton2.setEnabled(False)
                self.stopButton.setEnabled(False)
                self.audioBox1.setTitle("")
                self.audioBox2.setTitle("")
                self.audioBox2.setEnabled(False)
                self.labelAudio2.setText("")
                self.labelNext.setText("")
                self.labelStop.setText("")
                self.testNumLabel.setText("¡Muchas Gracias!")
                self.labelAudio1.setText("Hacé click en Exportar para guardar los datos de tu test. No olvides adjuntar el archivo nuevamente en el Google Forms.")
                
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
            diff.append(round(stim.offset + stim.userCorrection, 1))
            
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([f, offset, uc, diff])

            




stimuli = []
frequencies = [63, 125, 4000, 8000]
offsets = [6, 4, -4, -6]
for f in frequencies:
    for offset in offsets:
        stim = Stimulus()
        stim.boostFrequency = f
        stim.offset = offset
        stim.filename=resource_path("STIMULI/"+str(f)+".wav")
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