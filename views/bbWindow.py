
# -*- coding: utf-8 -*-
"""
Pop-up window for user to select BB
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import PyQt5.QtGui
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
        self.p1 = self.win.addPlot(title="")

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
        self.win.show()

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
