
# -*- coding: utf-8 -*-
"""
Pop-up window for user to select BB and config
"""

import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal
import PyQt5.QtGui as QtGui
import numpy as np
import cv2




class BBWindow(QtGui.QWidget):
    boundingBox = pyqtSignal(tuple)

    def __init__(self, data, parent=None):
        super(BBWindow,self).__init__(parent)
        self.roipos = (0,0,0,0)

        # Interpret image data as row-major instead of col-major
        pg.setConfigOptions(imageAxisOrder='row-major')

        pg.mkQApp()
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle('Bounding Box Selection')

        # A plot area (ViewBox + axes) for displaying the image
        self.p1 = self.win.addPlot(title="", row=0, col=0)

        # Item for displaying image data
        self.img = pg.ImageItem()
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
            self.boundingBox.emit(self.roipos)
            print(self.roipos)
        self.win.btnstate = btnstate
        self.button.clicked.connect(self.win.btnstate)
        proxy.setWidget(self.button)

        self.p2 = self.win.addLayout(row=2, col=0)
        self.p2.addItem(proxy,row=1,col=1)

        # win.resize(800, 800)
        

        # Get data
        height = data.shape[0]
        self.img.setImage(data)

        def imageHoverEvent(event):
            """Show the position, pixel, and value under the mouse cursor.
            """
            if event.isExit():
                self.p1.setTitle("")
                return
            pos = event.pos()
            cursor_i, cursor_j = pos.x(), pos.y()
            cursor_i = int(np.clip(cursor_i, 0, data.shape[1] - 1))
            cursor_j = int(np.clip(cursor_j, 0, data.shape[0] - 1))
            # val = data[cursor_j, cursor_i]

            # roipos = ((ax0Start, ax0Stop), (ax1Start, ax1Stop))
            # ax0 = y; ax1 = x; roipos = ((y1,y2),(x1,x2))
            roipos, _ = self.roi.getArraySlice(data, self.img, axes=(0,1), returnSlice=False)
            roipos = [[x, rest] for x, rest in roipos]
            roipos = [item for sublist in roipos for item in sublist]
            x, y, w, h = roipos[2],roipos[0],roipos[3]-roipos[2],roipos[1]-roipos[0]
            self.roipos = (x, y, w, h)
            
            self.p1.setTitle(f"cursor position: {cursor_i, cursor_j}  roi: {x,y,w,h}")

        # Monkey-patch the image to use our custom hover function. 
        # This is generally discouraged (you should subclass ImageItem instead),
        # but it works for a very simple use like this. 
        self.img.hoverEvent = imageHoverEvent

        self.img.scale(0.2, 0.2)
        self.img.translate(-50, 0)

        # zoom to fit image
        self.p1.autoRange()

        # self.win.show()



import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

class Parameter_Tree(ParameterTree):
    def __init__(self):
        super().__init__()
        self.params = [
            {'name': 'Parameters', 'type': 'group', 'children': 
                [
                    {'name': 'Video FPS', 'type': 'float', 'value': 0.1, 'step': 0.01},
                    {'name': 'Pressure Log Read FPS', 'float': 'float', 'value': 0.2, 'step': 0.01},
                    {'name': 'Video Path', 'type': 'str', 'value': "resources/testing.avi"},
                    {'name': 'Pressure Log Path', 'type': 'str', 'value': "resources/pressure.csv"},
                    {'name': 'Pressure Log Start', 'type': 'float', 'value': 0},
                    {'name': 'e-6m to pixel', 'type': 'float', 'value': 3.46},
                ]
            },
            {'name': 'Save/Restore functionality', 'type': 'group', 'children': [
                {'name': 'Save State', 'type': 'action'},
                {'name': 'Restore State', 'type': 'action'},
            ]}
        ]

        ## Create tree of Parameter objects
        self.p = Parameter.create(name='params', type='group', children=self.params)

        ## If anything changes in the tree, print a message
        def change(param, changes):
            print("tree changes:")
            for param, change, data in changes:
                path = p.childPath(param)
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
            for ch2 in child.children():
                ch2.sigValueChanging.connect(valueChanging)
                


        def save():
            global state
            state = self.p.saveState()
            
        def restore():
            global state
            self.p.restoreState(state)
        self.p.param('Save/Restore functionality', 'Save State').sigActivated.connect(save)
        self.p.param('Save/Restore functionality', 'Restore State').sigActivated.connect(restore)


        ## Create two ParameterTree widgets, both accessing the same data
        # self.t = ParameterTree()
        self.setParameters(self.p, showTop=False)
        self.setWindowTitle('pyqtgraph example: Parameter Tree')

        ## test save/restore
        self.s = self.p.saveState()
        self.p.restoreState(self.s)

class ConfigWindow(QtGui.QWidget):
    def __init__(self, frame, parent=None):
        super().__init__()
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        bbwin = BBWindow(frame).win
        param_tree = Parameter_Tree()
        self.layout.addWidget(bbwin, 0, 0)
        self.layout.addWidget(param_tree, 1,0)
        self.show()
        self.resize(800,800)

# ## Start Qt event loop unless running in interactive mode or using pyside.
# if __name__ == '__main__':
#     import sys
    
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()

