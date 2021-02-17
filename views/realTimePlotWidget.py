from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtWidgets
from pyqtgraph import PlotWidget

class RealTimePlotWidget(PlotWidget):
    def __init__(self, parent=None, x_len=200, y_range=[-0.5, 0.5]):
        PlotWidget.__init__(self, parent)
        # Range settings
        self._x_len_ = x_len
        self._y_range_ = y_range

        # Store two lists _x_ and _y_
        self._x_ = list(range(0, self._x_len_))
        self._y_ = [0] * self._x_len_
        self.curve = self.plot(pen='y')
    
    @pyqtSlot(float)
    def update_plot(self, dataFloat):
        y = 0
        if dataFloat is not None:
            y = dataFloat
        self._y_.append(y)                                  # Add new datapoint
        self._y_ = self._y_[-self._x_len_:]                 # Truncate list y
        self.curve.setData(self._x_,self._y_)