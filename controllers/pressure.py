import os
import numpy as np
import time

from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

class PressureThread(QThread):
    pressureFloat = pyqtSignal(float)

    def __init__(self, csv_path, readRate, pressureQueue):
        super(QThread,self).__init__()
        self.pressureQueue = pressureQueue
        self.running = False
        self.stopped = False
        self.readRate = readRate
        self.csv_path = csv_path

    def run(self):
        print('Pressure Thread triggered')
        self.running = True
        i = 0
        pressure_csv = read_pressure_csv(self.csv_path)
        while True:
            if self.running:
                time.sleep(1/self.readRate)
                pressure = pressure_csv[i]
                i = i+1
                self.pressureQueue.put(pressure)
                self.pressureFloat.emit(pressure)
            else:
                if self.stopped:
                    break
                else:
                    pass

    def _continue(self):
        self.running = True

    def _pause(self):
        self.running = False
    
    def _stop(self):
        self.stopped = True

def read_pressure_csv(filepath):
    pressure = np.genfromtxt(filepath, delimiter=',')
    pressure = pressure[~np.isnan(pressure)]
    return pressure