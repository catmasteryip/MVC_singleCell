from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import QtCore
from views.main_view_ui import Ui_MainWindow
from PyQt5.QtGui import QImage, QPixmap
import time


class MainView(QMainWindow):
    def __init__(self, model, main_controller):
        super().__init__()

        self._model = model
        self._main_controller = main_controller
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self.restart=False

        # control ui elements
        self._ui.startButton.clicked.connect(self.startButtonPressed)
        self._ui.stopButton.clicked.connect(self.stopButtonPressed)
        self._ui.pauseButton.clicked.connect(self.pauseButtonPressed)

        # connect ui elements to controller
        self._ui.startButton.clicked.connect(self._main_controller.startButtonPressed)
        self._ui.startButton.clicked.connect(self.startButtonPressed)

        self._ui.stopButton.clicked.connect(self._main_controller.stopButtonPressed)
        self._ui.stopButton.clicked.connect(self.stopButtonPressed)

        self._ui.resetBBButton.clicked.connect(self._main_controller.resetBBButtonPressed)
        # self._ui.resetBBButton.clicked.connect(self.resetBBButtonPressed)

        self._ui.pauseButton.clicked.connect(self._main_controller.pauseButtonPressed)


        # listen for model event signals
        self._model.frameSignal.connect(self.setImage)
        self._model.lengthText.connect(self.setLength)
        self._model.pressureText.connect(self.setPressure)
        self._model.agText.connect(self.setAg)
        self._model.pressureFloat.connect(self._ui.graphWidget.update_plot)
        self._model.lengthFloat.connect(self._ui.lengthGraphWidget.update_plot)

        
        # set a default values to controller
        self._ui.startButton.setEnabled(True)
        self._ui.stopButton.setEnabled(False)
        self._ui.pauseButton.setEnabled(False)


    @pyqtSlot(bool)
    def startButtonPressed(self):
        if self.restart:
            self.__init__()
        else:
            self._ui.startButton.setEnabled(False)
        self._ui.stopButton.setEnabled(True)
        self._ui.pauseButton.setEnabled(True)

    @pyqtSlot(bool)
    def stopButtonPressed(self):
        self._ui.startButton.setText('RESTART')
        self.restart = True
        self._ui.startButton.setEnabled(True)
        self._ui.stopButton.setEnabled(False)
        self._ui.pauseButton.setEnabled(True)

    @pyqtSlot(bool)
    def pauseButtonPressed(self):
        self._ui.startButton.setEnabled(True)
        self._ui.stopButton.setEnabled(True)
        self._ui.pauseButton.setEnabled(False)

    @pyqtSlot(object)
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