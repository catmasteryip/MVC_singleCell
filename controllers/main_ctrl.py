# MVC pattern-controller
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from controllers.computer_vision import CVThread
from controllers.pressure import PressureThread
from controllers.calculateAg import CalculateAgThread

from PyQt5.QtGui import QImage
import queue
import threading
import os
import sys


class MainController(QObject):

    def __init__(self, model):
        super().__init__()

        # Model initiation
        self._model = model

    def initSequence(self):
        # retrieve model params as defaults to init threads
        params = self._model.params

        # Queues initiation
        self.lengthQueue = queue.Queue()
        self.pressureQueue = queue.Queue()
        self.agQueue = queue.Queue()

        # Change video paths and pressure .csv paths
        # get path in executable
        # cwd = sys.executable.rsplit('/',1)[0]
        # get path in raw python code
        cwd = os.getcwd()
        vid_path = os.path.join(cwd,params['Video Path'][0])
        pressure_path = os.path.join(cwd,params['Pressure Log Path'][0])

        # CVThread initiation
        bb = eval(params['ROI'][0])
        self._cvThread = CVThread(lengthQueue = self.lengthQueue, vid_path=vid_path, fps = params['Video FPS'][0], initBB=bb)
        self._cvThread.changePixmap.connect(self.update_frame)
        self._cvThread.lengthFloat.connect(self.update_length)
        self._cvThread.rawFrame.connect(self.update_rawFrame)

        # PressureThread initiation
        self._pressureThread = PressureThread(csv_path=pressure_path,readRate=params['Pressure Read Rate'][0], 
        pressureQueue = self.pressureQueue)
        self._pressureThread.pressureFloat.connect(self.update_pressure)

        # ElasticityThread initiation
        self._calculateAgThread = CalculateAgThread(lengthQueue = self.lengthQueue,
                                                 pressureQueue = self.pressureQueue,
                                                 length_ratio = params['pixel to 1e-6m'][0],
                                                 agQueue = self.agQueue)
        self._calculateAgThread.agFloat.connect(self.update_ag)

    @pyqtSlot(object)
    def parameterSaved(self, params):
        # update model params
        self._model.params = params
        self.initSequence()
        
    @pyqtSlot()
    def configurationComplete(self):
        self._model.flag = 'configured'

    @pyqtSlot(bool)
    def startButtonPressed(self):
        if self._model.flag == 'configured':
            # start
            self._cvThread.start()
            self._pressureThread.start()
            self._calculateAgThread.start()
        elif self._model.flag == 'paused':
            # continue 
            self._cvThread._continue()
            self._pressureThread._continue()
            self._calculateAgThread._continue()
            self._model.flag = 'started'
        elif self._model.flag == 'stopped':
            print('mainCon: restarting')
            # restart
            self.initSequence()
            self._cvThread.start()
            self._pressureThread.start()
            self._calculateAgThread.start()
            self._model.flag = 'started'

    @pyqtSlot(bool)
    def pauseButtonPressed(self):
        print('pauseButtonPressed')
        self._cvThread._pause()
        self._pressureThread._pause()
        self._calculateAgThread._pause()
        self._model.flag = 'paused'

    @pyqtSlot(bool)
    def stopButtonPressed(self):
        print('stopButtonPressed')
        self._cvThread._stop()
        self._pressureThread._stop()
        self._calculateAgThread._stop()
        self._model.flag = 'stopped'

    @pyqtSlot(bool)
    def configButtonPressed(self):
        pass
        

    @pyqtSlot(tuple)
    def update_BB(self, boundingBox):
        self._model.boundingBox = boundingBox

    @pyqtSlot(object)
    def update_rawFrame(self, image):
        self._model.rawFrame = image

    @pyqtSlot(object)
    def update_frame(self, image):
        self._model.frame = image

    @pyqtSlot(float)
    def update_length(self, lengthFloat):
        self._model.length = lengthFloat

    @pyqtSlot(float)
    def update_pressure(self, pressureFloat):
        self._model.pressure = pressureFloat

    @pyqtSlot(float)
    def update_ag(self, agFloat):
        self._model.ag = agFloat