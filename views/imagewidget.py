from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtWidgets
from pyqtgraph.widgets import RawImageWidget
import pyqtgraph as pg
import numpy as np

class ImageWidget(RawImageWidget):
    def __init__(self, parent=None, x_len=200, y_range=[-0.5, 0.5]):
        RawImageWidget.__init__(self, parent)
        # Item for displaying image data
        blank = np.zeros([100,100,3],dtype=np.uint8)
        self.setImage(blank)

        # Custom ROI for selecting an image region
        # self.roi = pg.ROI([-8, 14], [6, 5])
        # self.roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        # self.roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        # self.addItem(self.roi)
        # self.roi.setZValue(10)  # make sure ROI is drawn above image

        self.show()
    
    @pyqtSlot(object)
    def _update_image_(self, image):
        self.setImage(image)