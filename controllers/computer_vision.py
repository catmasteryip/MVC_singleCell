# most important thread of all, computer vision thread which reads vids (for offline model),
# and apply CV techniques to measure the size of the cell in constriction channel
import cv2
import os
import numpy as np
import time
import math
import threading
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap


class CVThread(QThread):
    changePixmap = pyqtSignal(object)
    rawFrame = pyqtSignal(object)
    lengthFloat = pyqtSignal(float)

    def __init__(self, lengthQueue, vid_path, initBB, fps=10):
        super(QThread, self).__init__()
        self.lengthQueue = lengthQueue
        self.backSub_buffer = cv2.createBackgroundSubtractorKNN(
            dist2Threshold=100., detectShadows=False)
        self.initBB = initBB
        self.running = False
        self.stopped = False
        self.fps = fps
        self.vid_path = vid_path

    def run(self):
        print('CVThread triggered')
        self.running = True
        self.cv2_imagepipe(vid_path=self.vid_path,
                           initBB=self.initBB, fps=self.fps)
        self.exit()

    def _continue(self):
        self.running = True

    def _pause(self):
        self.running = False

    def _stop(self):
        self.running = False
        self.stopped = True

    def cv2_imagepipe(self, vid_path, initBB, fps):
        """
        Get image from video via cv2, process frames and send results to QThread
        Args:
            vid_path(str): video path
            initBB(tuple): dimensions of the tube
        """
        # python takes root as cwd
        cap = cv2.VideoCapture(vid_path)
        backSub = self.backSub_buffer
        while True:
            if self.running:
                ret, rawFrame = cap.read()
                if ret:
                    """
                    Special comments:
                    computer_vision function converts frame
                    """
                    raw = rawFrame.copy()
                    time.sleep(1/fps)
                    frame, protrusion_length = self.computer_vision(
                        raw, backSub, initBB)

                    # https://stackoverflow.com/a/55468544/6622587
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    p = cv2Qt(rgbImage)

                    self.changePixmap.emit(p)
                    self.rawFrame.emit(rawFrame)
                    self.lengthFloat.emit(protrusion_length)
                    self.lengthQueue.put(protrusion_length)
                else:
                    cap = cv2.VideoCapture(vid_path)
                backSub = self.backSub_buffer
            else:
                if self.stopped:
                    break
                else:
                    pass

    def computer_vision(self, frame, backSub, initBB):
        """
        Measure protrusion length of the cell in a cv2 bgr image
        Args:
            frame(ndarray): cv2 bgr image
            backSub: cv2 background subtraction object
            initBB: tube area coordinates information
        Returns:
            output(ndarray): processed cv2 bgr image
            protrusion_length(float): instanteneous protrusion length
        """

        tubeX, tubeY, tubeW, tubeH = initBB
        output = frame.copy()

        # show tube bounding box on screen
        cv2.rectangle(output, (tubeX, tubeY),
                      (tubeX+tubeW, tubeY+tubeH), (255, 0, 0), 2)
        cv2.putText(output, f'Tube',
                    (tubeX, tubeY-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(output, f'Tube location (px): {tubeX,tubeY,tubeW,tubeH}',
                    (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        tubeFrame = frame[tubeY:tubeY+tubeH, tubeX:tubeX+tubeW]

        tubeGray = cv2.cvtColor(tubeFrame, cv2.COLOR_BGR2GRAY)

        # background subtraction
        foreground = backSub.apply(tubeGray)
        fg_mask = np.argwhere(foreground >= 127)
        fgGray = cv2.cvtColor(foreground, cv2.COLOR_GRAY2BGR)
        tube = tubeFrame

        protrusion_length = math.nan
        if len(fg_mask) > 0:
            cellY1 = np.min(fg_mask[:, 0])
            cellX1 = np.min(fg_mask[:, 1])
            cellY2 = np.max(fg_mask[:, 0])
            cellX2 = np.max(fg_mask[:, 1])
            cellW = cellX2-cellX1
            cellH = cellY2-cellY1
            if tubeFrame.shape[0]*0.5 < cellH:
                if tubeFrame.shape[1]*0.1 < cellW < tubeFrame.shape[1]*0.9:
                    cv2.rectangle(tube, (cellX1, cellY1),
                                  (cellX2, cellY2), (0, 127, 255), 2)
                    protrusion_length = cellX2-cellX1

        output = np.concatenate((output, rescale(tube, output)), axis=0)
        output = np.concatenate((output, rescale(fgGray, output)), axis=0)

        return output, protrusion_length


def rescale(img2, img1):
    width = int(img1.shape[1])
    scale_percent = img1.shape[1]/img2.shape[1]
    height = int(img2.shape[0] * scale_percent)
    dim = (width, height)
    # resize image
    resized = cv2.resize(img2, dim, interpolation=cv2.INTER_AREA)
    return resized


def cv2Qt(rgbImage):
    h, w, ch = rgbImage.shape
    bytesPerLine = ch * w
    convertToQtFormat = QImage(
        rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
    return p
