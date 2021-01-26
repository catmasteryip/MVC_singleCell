from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QImage


class Model(QObject):
    frameSignal = pyqtSignal(QImage)
    lengthText = pyqtSignal(str)
    lengthFloat = pyqtSignal(float)
    pressureText = pyqtSignal(str)
    pressureFloat = pyqtSignal(float)
    agText = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._frame = None
        self._length = None
        self._pressure = None
        self._ag = None

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, p):
        self._frame = p
        self.frameSignal.emit(p)

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._length = length
        self.lengthFloat.emit(length)
        self.lengthText.emit(f'{length}')

    @property
    def pressure(self):
        return self._pressure

    @pressure.setter
    def pressure(self, pressure):
        self._pressure = pressure
        self.pressureText.emit(f'{pressure}')
        self.pressureFloat.emit(pressure)

    @property
    def ag(self):
        return self._ag

    @ag.setter
    def ag(self, ag):
        self._ag = ag
        self.agText.emit(f'{ag}')

    