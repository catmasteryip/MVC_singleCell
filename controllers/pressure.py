import os
import numpy as np
import time

from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

class PressureThread(QThread):
    pressureFloat = pyqtSignal(float)

    def __init__(self, pressureQueue):
        super(QThread,self).__init__()
        self.pressureQueue = pressureQueue
        self.running = False
        self.stopped = False

    def run(self):
        i = 0
        pressure_csv = read_pressure_csv('resources/pressure.csv')
        while True:
            if self.running:
                time.sleep(0.1)
                pressure = pressure_csv[i]
                i = i+1
                self.pressureQueue.put(pressure)
                self.pressureFloat.emit(pressure)
            else:
                if self.stopped:
                    break
                else:
                    pass

    def start(self):
        self.running = True

    def stop(self):
        self.stopped = True

    def pause(self):
        self.running = False

def read_pressure_csv(filepath):
    pressure = np.genfromtxt(filepath, delimiter=',')
    pressure = pressure[~np.isnan(pressure)]
    return pressure