from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from controllers.computer_vision import CVThread
from controllers.pressure import PressureThread
from controllers.calculateAg import CalculateAgThread
from views.configWindow import ConfigWindow
from PyQt5.QtGui import QImage
import queue
import threading


class MainController(QObject):

    def __init__(self, model):
        super().__init__()
        # Queues initiation
        self.lengthQueue = queue.Queue()
        self.pressureQueue = queue.Queue()
        self.agQueue = queue.Queue()


        # Model initiation
        self._model = model

        # CVThread initiation
        self._cvThread = CVThread(lengthQueue = self.lengthQueue)
        self._cvThread.changePixmap.connect(self.update_frame)
        self._cvThread.lengthFloat.connect(self.update_length)
        self._cvThread.rawFrame.connect(self.update_rawFrame)

        # PressureThread initiation
        self._pressureThread = PressureThread(pressureQueue = self.pressureQueue)
        self._pressureThread.pressureFloat.connect(self.update_pressure)

        # ElasticityThread initiation
        self._calculateAgThread = CalculateAgThread(lengthQueue = self.lengthQueue,
                                                 pressureQueue = self.pressureQueue,
                                                 length_ratio = 3.46,
                                                 agQueue = self.agQueue)
        self._calculateAgThread.agFloat.connect(self.update_ag)

        self._cvThread.start()
        self._pressureThread.start()
        self._calculateAgThread.start()

        # controller-subcontroller connections

    @pyqtSlot(bool)
    def startButtonPressed(self):
        print('startButtonPressed')
        self._cvThread._start()
        self._pressureThread.start()
        # print(f'{self._cvThread.isRunning()}')

    @pyqtSlot(bool)
    def stopButtonPressed(self):
        print('stopButtonPressed')
        self._cvThread._stop()
        self._pressureThread.stop()

    @pyqtSlot(bool)
    def pauseButtonPressed(self):
        print('pauseButtonPressed')
        self._cvThread.pause()
        self._pressureThread.pause()

    @pyqtSlot(bool)
    def configButtonPressed(self):
        print('configButtonPressed')
        self._cvThread._stop()
        self._pressureThread.stop()
        self.configWindow = ConfigWindow(self._model.rawFrame)
        self.configWindow.boundingBox.connect(self.update_BB)

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