# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_view_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageLabel.setGeometry(QtCore.QRect(40, 60, 361, 281))
        self.imageLabel.setObjectName("imageLabel")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(220, 400, 274, 80))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.lengthLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lengthLabel.setObjectName("lengthLabel")
        self.gridLayout.addWidget(self.lengthLabel, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 2, 1, 1)
        self.lengthLabel_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lengthLabel_3.setObjectName("lengthLabel_3")
        self.gridLayout.addWidget(self.lengthLabel_3, 1, 0, 1, 1)
        self.lengthLabel_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lengthLabel_2.setObjectName("lengthLabel_2")
        self.gridLayout.addWidget(self.lengthLabel_2, 0, 0, 1, 1)
        self.pressureLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.pressureLabel.setObjectName("pressureLabel")
        self.gridLayout.addWidget(self.pressureLabel, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.agLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.agLabel.setObjectName("agLabel")
        self.gridLayout.addWidget(self.agLabel, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 2, 1, 1)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(420, 60, 301, 281))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lengthGraphWidget = realTimePlotWidget(self.gridLayoutWidget_2)
        self.lengthGraphWidget.setObjectName("lengthGraphWidget")
        self.gridLayout_2.addWidget(self.lengthGraphWidget, 2, 0, 1, 1)
        self.graphWidget = realTimePlotWidget(self.gridLayoutWidget_2)
        self.graphWidget.setObjectName("graphWidget")
        self.gridLayout_2.addWidget(self.graphWidget, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.imageLabel.setText(_translate("MainWindow", "imageLabel"))
        self.lengthLabel.setText(_translate("MainWindow", "lengthLabel"))
        self.label.setText(_translate("MainWindow", " e-6m"))
        self.label_2.setText(_translate("MainWindow", "in H2O"))
        self.lengthLabel_3.setText(_translate("MainWindow", "Pressure inH2O"))
        self.lengthLabel_2.setText(_translate("MainWindow", "Protrusion Length"))
        self.pressureLabel.setText(_translate("MainWindow", "pressureLabel"))
        self.label_3.setText(_translate("MainWindow", "Ag"))
        self.agLabel.setText(_translate("MainWindow", "agLabel"))
        self.label_4.setText(_translate("MainWindow", "(Unit)"))

from views.plotwidget import realTimePlotWidget
