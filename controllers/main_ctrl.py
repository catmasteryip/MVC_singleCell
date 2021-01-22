from PyQt5.QtCore import QObject, pyqtSlot
from controllers.computer_vision import CVThread
from controllers.pressure import PressureThread
from controllers.calculateAg import CalculateAgThread
from PyQt5.QtGui import QImage
import queue


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

        # PressureThread initiation
        self._pressureThread = PressureThread(pressureQueue = self.pressureQueue)
        self._pressureThread.pressureFloat.connect(self.update_pressure)

        # ElasticityThread initiation
        self._calculateAgThread = CalculateAgThread(lengthQueue = self.lengthQueue,
                                                 pressureQueue = self.pressureQueue,
                                                 length_ratio = 3.46,
                                                 agQueue = self.agQueue)

        
        self._cvThread.start()
        self._pressureThread.start()
        self._calculateAgThread.start()

    @pyqtSlot(QImage)
    def update_frame(self, frameQImage):
        self._model.frame = frameQImage

    @pyqtSlot(float)
    def update_length(self, lengthFloat):
        self._model.length = lengthFloat

    @pyqtSlot(float)
    def update_pressure(self, pressureFloat):
        self._model.pressure = pressureFloat