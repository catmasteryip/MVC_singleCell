from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore
from views.main_view_ui import Ui_MainWindow
from PyQt5.QtGui import QImage, QPixmap
from views.mplwidget import MplCanvas


class MainView(QMainWindow):
    def __init__(self, model, main_controller):
        super().__init__()

        self._model = model
        self._main_controller = main_controller
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        # override lengthGraphWidget

        # connect ui elements to controller


        # listen for model event signals
        self._model.frameSignal.connect(self.setImage)
        self._model.lengthText.connect(self.setLength)
        self._model.pressureText.connect(self.setPressure)
        self._model.pressureFloat.connect(self._ui.graphWidget.myFig._update_canvas_)
        self._model.lengthFloat.connect(self._ui.lengthGraphWidget.myFig._update_canvas_)
        
        # set a default values to controller

    @pyqtSlot(QImage)
    def setImage(self, image):
        w = self._ui.imageLabel.width()
        h = self._ui.imageLabel.height()
        self._ui.imageLabel.setPixmap(QPixmap.fromImage(image).scaled(w,h,QtCore.Qt.KeepAspectRatio))

    @pyqtSlot(str)
    def setLength(self, lengthText):
        self._ui.lengthLabel.setText(lengthText)

    @pyqtSlot(str)
    def setPressure(self, pressureText):
        self._ui.pressureLabel.setText(pressureText)

    @pyqtSlot(str)
    def setAg(self, agText):
        self._ui.agLabel.setText(agText)