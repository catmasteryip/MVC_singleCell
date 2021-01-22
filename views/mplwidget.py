# Imports
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib
import numpy as np

# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')

# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, x_len=20, y_range=[-0.5, 0.5]):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.lyt = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.setLayout(self.lyt)

        # 2. Place the matplotlib figure
        self.myFig = MplCanvas(x_len = x_len, y_range=y_range)
        self.lyt.addWidget(self.myFig)

        # 3. Show
        self.show()
        return

class MplCanvas(FigureCanvas):
    '''
    This is the FigureCanvas in which the live plot is drawn.

    '''
    def __init__(self, x_len:int, y_range:list) -> None:
        '''
        :param x_len:       The nr of data points shown in one plot.
        :param y_range:     Range on y-axis.
        :param interval:    Get a new datapoint every .. milliseconds.

        '''
        super().__init__(Figure())
        # Range settings
        self._x_len_ = x_len
        self._y_range_ = y_range

        # Store two lists _x_ and _y_
        self._x_ = list(range(0, self._x_len_))
        self._y_ = [0] * self._x_len_

        # Store a figure ax
        self._ax_ = self.figure.subplots()
        self._ax_.set_ylim(ymin=self._y_range_[0], ymax=self._y_range_[1]) # added
        self._line_, = self._ax_.plot(self._x_, self._y_)                  # added
        self.draw()                                                        # added
        return

    @pyqtSlot(float)
    def _update_canvas_(self, pressureFloat) -> None:
        '''
        This function gets called on-demand by pyqtSignal

        '''
        with open("logs.txt", "a") as f:
                f.write(f"""
                {self._y_}
                """)
                f.close()
        y = 0
        if pressureFloat is not None:
            y = pressureFloat
        self._y_.append(y)

        # self._y_.append(round(get_next_datapoint(), 2))     # Add new datapoint
        self._y_ = self._y_[-self._x_len_:]                 # Truncate list y
        

        # New code
        # ---------
        self._line_.set_ydata(self._y_)
        
        y = np.array(self._y_)
        y = y[~np.isnan(y)]
        if sum(y) > 0:
            y_min = min(y)
            y_max = max(y)
            self._y_range_ = [ y_min-y_min/10, y_max+y_max/10 ]
            
        self._ax_.set_ylim(ymin=self._y_range_[0], ymax=self._y_range_[1])  # update y_lim
            
        self._ax_.draw_artist(self._ax_.patch)
        self._ax_.draw_artist(self._line_)
        self.update()
        self.flush_events()
        return