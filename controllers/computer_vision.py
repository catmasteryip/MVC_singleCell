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
from numpy.core.arrayprint import _leading_trailing
from scipy.ndimage import median_filter


class CVThread(QThread):
    changePixmap = pyqtSignal(object)
    rawFrame = pyqtSignal(object)
    lengthFloat = pyqtSignal(float)

    def __init__(self, lengthQueue, vid_path, initBB, fps=10):
        super(QThread, self).__init__()
        self.lengthQueue = lengthQueue
        # self.backSub_buffer = cv2.createBackgroundSubtractorKNN(
        #     dist2Threshold=100., detectShadows=False)
        self.backSub_buffer = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
        self.initBB = initBB
        self.running = False
        self.stopped = False
        self.fps = fps
        self.vid_path = vid_path
        self.cap = cv2.VideoCapture(self.vid_path)

    def run(self):
        print('CVThread triggered')
        self.running = True
        self.cv2_imagepipe(cap=self.cap,
                           initBB=self.initBB, fps=self.fps)
        self.exit()

    def _continue(self):
        self.running = True

    def _pause(self):
        self.running = False

    def _stop(self):
        self.running = False
        self.stopped = True

    def cv2_imagepipe(self, cap, initBB, fps):
        """
        Get image from video via cv2, process frames and send results to QThread
        Args:
            vid_path(str): video path
            initBB(tuple): dimensions of the tube
        """
        # python takes root as cwd
        self.cap = cap
        # backSub = self.backSub_buffer
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
                        raw, self.backSub_buffer, initBB)

                    # https://stackoverflow.com/a/55468544/6622587
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    p = cv2Qt(rgbImage)

                    self.changePixmap.emit(p)
                    self.rawFrame.emit(rawFrame)
                    self.lengthFloat.emit(protrusion_length)
                    self.lengthQueue.put(protrusion_length)
                else:
                    cap = cv2.VideoCapture(self.vid_path)
                # backSub = self.backSub_buffer
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
        
        tubeGray = median_filter(tubeGray, size=3)

        # background subtraction
        foreground = backSub.apply(tubeGray, learningRate=0)

        #blur
        foreground = cv2.GaussianBlur(foreground, (7, 7), 0)
        #fill holes
        foreground = FillHole(foreground)


        # foreground = np.argwhere(foreground >= 127)
        # fgGray = cv2.cvtColor(foreground, cv2.COLOR_GRAY2BGR)
        # tube = tubeFrame

        

        ret, thresh = cv2.threshold(foreground, 127, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        grayBGR = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        protrusion_length = math.nan
        if len(contours) != 0:
            # draw in blue the contours that were founded
            cv2.drawContours(grayBGR, contours, -1, (255,0,0), 1)

            # find the biggest countour (c) by the area
            c = max(contours, key = cv2.contourArea)
            x,y,w,h = cv2.boundingRect(c)
            print(w,tubeFrame.shape[1])

            if tubeFrame.shape[1]*0.1 < w < tubeFrame.shape[1]*0.9:
                protrusion_length = w
                # draw the biggest contour (c) in green
                cv2.rectangle(grayBGR,(x,y),(x+w,y+h),(0,255,0),2)

        

        output = np.concatenate((output, rescale(tubeFrame, output)), axis=0)
        output = np.concatenate((output, rescale(grayBGR, output)), axis=0)

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

def FillHole(img):
  # im_in = cv2.imread(imgPath, cv2.IMREAD_GRAYSCALE);
  # im_in = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  im_in = img
  # cv2.imwrite("im_in.png", im_in)
  # 复制 im_in 图像
  im_floodfill = im_in.copy()

  # Mask 用于 floodFill，官方要求长宽+2
  h, w = im_in.shape[:2]
  # print(im_in.shape)
  mask = np.zeros((h + 2, w + 2), np.uint8)

  # floodFill函数中的seedPoint对应像素必须是背景
  isbreak = False
  for i in range(im_floodfill.shape[0]):
      for j in range(im_floodfill.shape[1]):

          if (im_floodfill[i][j] == 0):
              seedPoint = (i, j)
              isbreak = True
              # print(im_floodfill[i][j])
              # print(seedPoint)
              break
          else:
              seedPoint = (0, 0)
              # print("seedPoint not found ")
              break
      if (isbreak):
          break

  # 得到im_floodfill 255填充非孔洞值
  cv2.floodFill(im_floodfill, mask, seedPoint, 255,cv2.FLOODFILL_MASK_ONLY)

  # 得到im_floodfill的逆im_floodfill_inv
  im_floodfill_inv = cv2.bitwise_not(im_floodfill)

  # 把im_in、im_floodfill_inv这两幅图像结合起来得到前景
  im_out = im_in | im_floodfill_inv

  # 保存结果
  # cv2.imwrite(SavePath, im_out)
  return im_out