# MVC pattern-another view
# complicated 2-line plots for curve fitting of protrusion length
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtWidgets
from pyqtgraph import PlotWidget
from pyqtgraph import mkPen


class TwoLineRealTimePlotWidget(PlotWidget):
    def __init__(self, parent=None, x_len=200, y_range=[-0.5, 0.5]):
        PlotWidget.__init__(self, parent)
        # Range settings
        self._x_len_ = x_len
        self._y_range_ = y_range

        # Store three lists
        self._x_ = list(range(0, self._x_len_))
        self._y1_ = self._yfit_ = [0] * self._x_len_
        # self.addLine(x=, y=None, pen=mkPen('r',width=3))
        self.curve1 = self.plot(pen='y')
        self.curveFit = self.plot(pen=mkPen('r'))

    @pyqtSlot(object)
    def update_plot(self, curveFittingPacket):
        print("widget: ", curveFittingPacket)
        self._x_ = curveFittingPacket.x
        self._x_len_ = len(self._x_)
        self._y1_ = curveFittingPacket.y
        self._yfit_ = curveFittingPacket.yfit
        self.curve1.setData(self._x_, self._y1_)
        self.curveFit.setData(self._x_, self._yfit_)

    def clear_plot(self):
        self._y1_ = self._yfit_ = [0] * self._x_len_
        self.curve1.setData(self._x_, self._y1_)
        self.curveFit.setData(self._x_, self._yfit_)
