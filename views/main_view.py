from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import QtCore
from views.main_view_ui import Ui_MainWindow
from PyQt5.QtGui import QImage, QPixmap
from views.configWindow import ConfigWindow
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

        # connect ui elements to model

        self._ui.startButton.clicked.connect(self._main_controller.startButtonPressed)
        self._ui.startButton.clicked.connect(self.startButtonPressed)

        self._ui.pauseButton.clicked.connect(self._main_controller.pauseButtonPressed)
        self._ui.pauseButton.clicked.connect(self.pauseButtonPressed)

        self._ui.stopButton.clicked.connect(self._main_controller.stopButtonPressed)
        self._ui.stopButton.clicked.connect(self.stopButtonPressed)

        self._ui.configButton.clicked.connect(self._main_controller.configButtonPressed)
        self._ui.configButton.clicked.connect(self.configButtonPressed)


        # listen for model event signals, i.e. link this view to model
        self._model.frameSignal.connect(self.setImage)
        self._model.lengthText.connect(self.setLength)
        self._model.pressureText.connect(self.setPressure)
        self._model.agText.connect(self.setAg)
        self._model.pressureFloat.connect(self._ui.graphWidget.update_plot)
        self._model.lengthFloat.connect(self._ui.lengthGraphWidget.update_plot)
        self._model.configComplete.connect(self.configComplete)

        
        # set a default values to controller
        self._ui.startButton.setEnabled(False)
        self._ui.stopButton.setEnabled(False)
        self._ui.pauseButton.setEnabled(False)
        self._ui.configButton.setEnabled(False)

        # starting sequence
        self.configWindow = ConfigWindow()
        self.configWindow.param_tree.parameters.connect(self._main_controller.parameterSaved)
        self.configWindow.closing.connect(self._main_controller.configurationComplete)


    @pyqtSlot(bool)
    def startButtonPressed(self):
        print('startButtonPressed')
        self._ui.startButton.setEnabled(False)
        self._ui.stopButton.setEnabled(True)
        self._ui.pauseButton.setEnabled(True)
        self._ui.configButton.setEnabled(False)

    @pyqtSlot(bool)
    def pauseButtonPressed(self):
        self._ui.startButton.setText('CONTINUE')
        self._ui.startButton.setEnabled(True)
        self._ui.stopButton.setEnabled(True)
        self._ui.pauseButton.setEnabled(False)

    @pyqtSlot(bool)
    def stopButtonPressed(self):
        self._ui.startButton.setText('RESTART')
        self._ui.startButton.setEnabled(True)
        self._ui.stopButton.setEnabled(False)
        self._ui.pauseButton.setEnabled(True)
        self._ui.configButton.setEnabled(True)

    @pyqtSlot(bool)
    def configButtonPressed(self):
        self._ui.startButton.setText('START')
        self._ui.startButton.setEnabled(False)
        self._ui.stopButton.setEnabled(False)
        self._ui.pauseButton.setEnabled(False)
        self._ui.configButton.setEnabled(False)

        self.configWindow = ConfigWindow(self._model.rawFrame)
        self.configWindow.param_tree.parameters.connect(self._main_controller.parameterSaved)
        self.configWindow.closing.connect(self._main_controller.configurationComplete)

    @pyqtSlot()
    def configComplete(self):
        self._ui.startButton.setText('START')
        self._ui.startButton.setEnabled(True)
        self._ui.stopButton.setEnabled(False)
        self._ui.pauseButton.setEnabled(False)
        self._ui.configButton.setEnabled(True)

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