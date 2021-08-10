
# -*- coding: utf-8 -*-
"""
Pop-up window for user to select BB and config
"""

import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import PyQt5.QtGui as QtGui
import numpy as np
import cv2




class BBWindow(QtGui.QWidget):
    boundingBox = pyqtSignal(tuple)

    def __init__(self, data, parent=None):
        super(BBWindow,self).__init__(parent)
        self.data = data
        self.roi = (0,0,0,0)

        # Interpret image data as row-major instead of col-major
        pg.setConfigOptions(imageAxisOrder='row-major')

        pg.mkQApp()
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle('Bounding Box Selection')

        # A plot area (ViewBox + axes) for displaying the image
        self.p1 = self.win.addPlot(title="", row=0, col=0)

        # Item for displaying image data
        self.img = roiImage()
        self.p1.addItem(self.img)

        # Custom ROI for selecting an image region
        self.roi = pg.ROI([0,0], [100,50])
        self.roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        self.roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.p1.addItem(self.roi)
        self.roi.setZValue(10)  # make sure ROI is drawn above image

        # add button to set initBB
        proxy = QtGui.QGraphicsProxyWidget()
        self.button = QtGui.QPushButton('ResetBB')

        # self.win.resetBB = resetBB
        def btnstate():
            # save initBB and send to controller
            roipos, _ = self.roi.getArraySlice(self.data , self.img, axes=(0,1), returnSlice=False)
            roipos = [[x, rest] for x, rest in roipos]
            roipos = [item for sublist in roipos for item in sublist]
            x, y, w, h = roipos[2],roipos[0],roipos[3]-roipos[2],roipos[1]-roipos[0]
            self.roi = (x, y, w, h)
            self.boundingBox.emit(self.roi)
            print(self.roi)

        self.win.btnstate = btnstate
        self.button.clicked.connect(self.win.btnstate)
        proxy.setWidget(self.button)

        self.p2 = self.win.addLayout(row=2, col=0)
        self.p2.addItem(proxy,row=1,col=1)

        # win.resize(800, 800)
        

        # Get data
        self.img.update_image(data)

        self.img.scale(0.2, 0.2)
        self.img.translate(-50, 0)

        # zoom to fit image
        self.p1.autoRange()

        # self.win.show()
    
    @pyqtSlot(object)
    def update_data(self, params):
        
        video_path = params['Video Path'][0]
        print(f'triggered: {video_path}')
        cap = cv2.VideoCapture(video_path)
        ret, rawFrame = cap.read()
        if ret:
            self.data = rawFrame
            self.img.update_image(self.data)
        else:
            print('Video does not exist/Wrong Path/Video corrupted')

class roiImage(pg.ImageItem):
    def __init__(self):
        super().__init__()
        self.image = None
        self.roipos = None
        self.cursor_i = None
        self.cursor_j = None

    def update_image(self, image):
        self.image = image
        self.setImage(image)
        self.hoverEvent = self.imageHoverEvent

    def imageHoverEvent(self, event):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.isExit():
            return
        pos = event.pos()
        cursor_i, cursor_j = pos.x(), pos.y()
        self.cursor_i = int(np.clip(cursor_i, 0, self.image.shape[1] - 1))
        self.cursor_j = int(np.clip(cursor_j, 0, self.image.shape[0] - 1))


import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

class Parameter_Tree(ParameterTree):
    parameters = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.params = [
                    {'name': 'Video FPS', 'type': 'float', 'value': 10, 'step': 0.01},
                    {'name': 'Video Path', 'type': 'str', 'value': "resources/testing.avi"},
                    # {'name': 'Video Path', 'type': 'str', 'value': "resources/350-390.avi"},
                    {'name': 'Pressure Read Rate', 'float': 'float', 'value': 5, 'step': 0.01},
                    {'name': 'Pressure Log Path', 'type': 'str', 'value': "resources/pressure.csv"},
                    {'name': 'Pressure Log Start', 'type': 'float', 'value': 0},
                    {'name': 'pixel to 1e-6m', 'type': 'float', 'value': 3.46},
                    {'name': 'ROI', 'type': 'str', 'value': '(852,500,243,100)','readonly': True},
                    {'name': 'Save State', 'type': 'action'},
                    {'name': 'Restore State', 'type': 'action'}
                ]

        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=self.params)

        ## If anything changes in the tree, print a message
        def change(param, changes):
            print("tree changes:")
            for param, change, data in changes:
                path = self.p.childPath(param)
                if path is not None:
                    childName = '.'.join(path)
                else:
                    childName = param.name()
                print('  parameter: %s'% childName)
                print('  change:    %s'% change)
                print('  data:      %s'% str(data))
                print('  ----------')
            
        self.p.sigTreeStateChanged.connect(change)


        def valueChanging(param, value):
            print("Value changing (not finalized): %s %s" % (param, value))
            
        # Too lazy for recursion:
        for child in self.p.children():
            child.sigValueChanging.connect(valueChanging)
            # for ch2 in child.children():
            #     ch2.sigValueChanging.connect(valueChanging)
                


        def save():
            global state
            state = self.p.saveState()
            
            params = self.p.getValues()
            self.parameters.emit(params)
            
                    
            
        def restore():
            global state
            self.p.restoreState(state)
        
        self.p.param('Save State').sigActivated.connect(save)
        self.p.param('Restore State').sigActivated.connect(restore)


        ## Create two ParameterTree widgets, both accessing the same data
        self.setParameters(self.p, showTop=False)
        self.setWindowTitle('pyqtgraph example: Parameter Tree')

        ## test save/restore
        s = self.p.saveState()
        self.p.restoreState(s)

    @pyqtSlot(tuple)
    def updateBB(self, roi):
        roi = str(roi)
        self.p.param('ROI').setValue(roi)
        print(roi)

from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import QEvent

class ConfigWindow(QtGui.QWidget):
    closing = pyqtSignal()
    def __init__(self, frame=np.zeros((100,100,3)), parent=None):
        super().__init__()
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.bbWidget = BBWindow(frame)
        self.bbwin = self.bbWidget.win
        self.param_tree = Parameter_Tree()

        # get video path from param_tree
        self.param_tree.parameters.connect(self.bbWidget.update_data)
        # connect updateBB to param_tree
        self.bbWidget.boundingBox.connect(self.param_tree.updateBB)

        self.layout.addWidget(self.param_tree, 0, 0)
        self.layout.addWidget(self.bbwin, 1,0)
        self.show()
        self.resize(800,800)

    def closeEvent(self, event: QCloseEvent):
        self.closing.emit()
        return super().closeEvent(event)


# ## Start Qt event loop unless running in interactive mode or using pyside.
# if __name__ == '__main__':
#     import sys
#     app = QtGui.QApplication([])
#     win = ConfigWindow()
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()


