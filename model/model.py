# MVC pattern model
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QImage


class Model(QObject):
    frameSignal = pyqtSignal(object)
    rawFrameSignal = pyqtSignal(object)
    lengthText = pyqtSignal(str)
    lengthFloat = pyqtSignal(float)
    pressureText = pyqtSignal(str)
    pressureFloat = pyqtSignal(float)
    agText = pyqtSignal(str)
    curveFittingPacket = pyqtSignal(object)
    configComplete = pyqtSignal()
    restarting = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._frame = None
        self._length = None
        self._pressure = None
        self._ag = None
        self._curveFitting = None
        self._rawFrame = None
        self._boundingBox = None
        self._flag = 'paused'
        self._params = None

    @property
    def curveFitting(self):
        return self._curveFitting

    @curveFitting.setter
    def curveFitting(self, curveFitting):
        print("model: ", curveFitting)
        self.curveFittingPacket.emit(curveFitting)

    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, flag):
        if flag == 'configured':
            self.configComplete.emit()
        elif flag == 'started':
            self.restarting.emit()
        self._flag = flag

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params

    @property
    def boundingBox(self):
        return self._boundingBox

    @boundingBox.setter
    def boundingBox(self, bb):
        self._boundingBox = bb
        # print(self._boundingBox)
        # self.boundingBox.emit(tuple)

    @property
    def rawFrame(self):
        return self._rawFrame

    @rawFrame.setter
    def rawFrame(self, p):
        self._rawFrame = p
        self.rawFrameSignal.emit(p)

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
