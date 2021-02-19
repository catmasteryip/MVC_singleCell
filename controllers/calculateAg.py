import os
import numpy as np
import math
import time
import sys
import traceback
import matplotlib.pyplot as plt
from moviepy.video.io.bindings import mplfig_to_npimage
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QImage, QPixmap

class CalculateAgThread(QThread):
    agFloat = pyqtSignal(float)

    def __init__(self, length_ratio, pressureQueue, lengthQueue, agQueue):
        super(QThread, self).__init__()
        self.data = Data()
        self.length_ratio = length_ratio
        self.empty_data = self.data
        self.pressureQueue = pressureQueue
        self.lengthQueue = lengthQueue
        self.agQueue = agQueue
        self.running = False
        self.stopped = False

    def run(self):
        self.running = True
        while True:
            if self.running:
                self.data.updatep(self.pressureQueue.get())
                l = self.lengthQueue.get()
                self.data.updatel(l)

                # with open("logs.txt", "a") as f:
                #         f.write(f"""
                #         l: {l}
                #         """)
                if (self.data.l.shape[0]) > 2:
                    if self.data.l[-2] > 0 and (math.isnan(self.data.l[-1]) or self.data.l[-1] < 1.):
                        # with open("logs.txt", "a") as f:
                        #     f.write(f"""
                        #     self.data.l: {self.data.l}
                        #     """)
                        Ag = self.calculateAg(self.data)
                        self.data = Data()
                        self.agFloat.emit(Ag)
                        self.agQueue.put(Ag)
            else:
                if self.stopped:
                    break
                else:
                    pass
                    
    def _continue(self):
        self.running = True

    def _pause(self):
        self.running = False
    
    def _stop(self):
        self.stopped = True

    def plotting(self):
        pass

    def calculateAg(self,data):
        try:
            l = data.l 
            ltime = data.ltime 
            p = data.p 
            ptime = data.ptime 
            length_ratio = self.length_ratio

            l = l/length_ratio
            

            # length data cleaning
            nan_indexes = np.argwhere(np.isnan(l))
            l = np.delete(l, nan_indexes)
            zero_indexes = np.argwhere(l == 0.)
            l = np.delete(l, zero_indexes)
            if len(l) < 10:
                return math.nan
            ltime = np.delete(ltime, nan_indexes)
            ltime = np.delete(ltime, zero_indexes)
            ltime_adj = ltime - ltime[0]

            # fitting 3rd order polynomial
            
            # z = np.polyfit(x=x, y=y, deg=3)
            # poly3 = np.poly1d(z)
            # xnew = np.linspace(0, max(x), num=50, endpoint=True)
            # ynew = poly3(xnew)

            # firstOrderCutoff = secondOrderCutoff = cutoff = len(x)
            # dydx = np.gradient(ynew,xnew)
            # if (dydx==0).any():
            #     firstOrderCutoff = np.where(dydx==0)[0][-1]

            # d2ydx2 = np.gradient(dydx, xnew)
            # secondOrderCutoff = np.where(np.diff(np.sign(d2ydx2))>0)[0]
            # cutoff = min(firstOrderCutoff,secondOrderCutoff)

            # y_cropped = y[x<xnew[cutoff]]
            # y_cropped = y_cropped[1:]
            # x_cropped = x[x<xnew[cutoff]]
            # x_cropped = x_cropped[1:]

            # take only first 10 datapoints
            x = ltime_adj
            y = l
            y_cropped = y[1:10]
            x_cropped = x[1:10]
            
            alpha,log_K = np.polyfit(np.log(x_cropped), np.log(y_cropped), 1)
            K = np.exp(log_K)
            l_fit = K*(x_cropped**alpha)

            # average pressure difference calculation
            tenter = min(ltime)
            tentry = max(ltime_adj)

            p = p[ptime>tenter]
            ptime = ptime[ptime>tenter]
            ptime = ptime-ptime[0]
            
            Ag = float(math.nan)      
            p_avg = np.trapz(x=ptime,y=p)*249.08/tentry
            Aj = K/1.848/p_avg
            Ag = 1/Aj/math.gamma(1+alpha)
            if Ag is None:
                Ag = float(math.nan)

            return round(Ag,3)

        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            # error list: np.linalg.LinAlgError
            with open("logs.txt", "a") as f:
                f.write(f"""
                x: {x}
                y: {y}
                x_cropped: {x_cropped}
                y_cropped: {y_cropped}
                exc_info: {exc_info}
                """)
                # {Ag} {Aj} {alpha} {p_avg}
                f.close()

    def cv2Qt(self, rgbImage):
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        return p

class Data():
    def __init__(self):
        self.p = np.array([])
        self.ptime = np.array([])
        self.ltime = np.array([])
        self.l = np.array([])

    def updatep(self,pressure):
        self.p = np.append(self.p,pressure)
        self.ptime = np.append(self.ptime,time.time())

    def updatel(self,length):
        self.l = np.append(self.l,length)
        self.ltime = np.append(self.ltime,time.time())