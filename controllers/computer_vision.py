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

import pybgs as bgs
from scipy.ndimage import median_filter
from keras.preprocessing import image

class CVThread(QThread):
    changePixmap = pyqtSignal(object)
    rawFrame = pyqtSignal(object)
    lengthFloat = pyqtSignal(float)

    def __init__(self, lengthQueue, vid_path, initBB, fps=10):
        super(QThread, self).__init__()
        self.lengthQueue = lengthQueue
        # self.backSub_buffer = cv2.createBackgroundSubtractorKNN(
        #     dist2Threshold=100., detectShadows=False)
        self.backSub_buffer = bgs.StaticFrameDifference()
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
                    print("vedio read error! please check vedio path again")
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
        # cv2.imwrite("tubeFrame/" + "frame.jpg", frame)
        # show tube bounding box on screen
        cv2.rectangle(output, (tubeX, tubeY),
                      (tubeX+tubeW, tubeY+tubeH), (255, 0, 0), 2)
        cv2.putText(output, f'Tube',
                    (tubeX, tubeY-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(output, f'Tube location (px): {tubeX,tubeY,tubeW,tubeH}',
                    (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        tubeFrame = frame[tubeY:tubeY+tubeH, tubeX:tubeX+tubeW]
        cv2.imwrite("tubeFrame/" + "tubeFrame.jpg", tubeFrame)
        tubeGray = cv2.cvtColor(tubeFrame, cv2.COLOR_BGR2GRAY)
        #apply filter
        tubeGray = median_filter(tubeGray,size=3)
        # background subtraction
        foreground = backSub.apply(tubeGray)
        #blur
        foreground = cv2.GaussianBlur(foreground, (7, 7), 0)
        # cv2.imwrite("tubeFrame/" + "before.jpg", foreground)
        #fill holes
        foreground = FillHole(foreground)
        # cv2.imwrite("tubeFrame/" + "after.jpg", foreground)
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
        # previous bounding box detection
        # output = np.concatenate((output, rescale(tube, output)), axis=0)
        # output = np.concatenate((output, rescale(fgGray, output)), axis=0)
        # return output, protrusion_length

        # new boundig box detection edited by xin in July 2021
        return find_boundingbox(output,foreground,tubeFrame)


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
def ymid(y, h):
    return y + int(h / 2)
def find_boundingbox(output,mask, tube):
    # img = cv2.imread("ori_preprocessing/31.jpg", cv2.IMREAD_GRAYSCALE)
    # img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # img = image.img_to_array(img, dtype='uint8')
    img = image.img_to_array(mask, dtype='uint8')
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    grad = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)

    _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]

    # identify lines (l=0, 1, ...) based on ymid() and estimate line width
    ym2l, l, l2w, rects = {}, 0, {}, []
    for cont in contours:
        x, y, w, h = cv2.boundingRect(cont)
        rects.append([x, y, w, h])
        ym = ymid(y, h)
        if ym not in ym2l:
            for i in range(-2, 3):  # range of ymid() values allowed for same line
                if ym + i not in ym2l:
                    ym2l[ym + i] = l
            l2w[l] = w
            l += 1
        else:
            l2w[ym2l[ym]] += w

    # combine rectangles for "good" lines (those close to maximum width)
    # print(l2w.values())
    maxw, l2r = max(l2w.values(), default=0), {}
    for x, y, w, h in rects:
        l = ym2l[ymid(y, h)]
        if l2w[l] > .9 * maxw:
            if l not in l2r:
                l2r[l] = [x, y, x + w, y + h]
            else:
                x1, y1, X1, Y1 = l2r[l]
                l2r[l] = [min(x, x1), min(y, y1), max(x + w, X1), max(y + h, Y1)]
    protrusion_length =0
    for x, y, X, Y in l2r.values():
        cv2.rectangle(img, (x, y), (X - 1, Y - 1), (255, 255, 255), 1)
        protrusion_length = X - 1 - x
        # print(x, y, X - 1, Y - 1)
        bounding = []
        bounding.append(x)
        bounding.append(y)
        bounding.append(X - 1)
        bounding.append(Y - 1)
    # cv2.imshow("img", img)
    # cv2.waitKey(0)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    fgGray = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    output = np.concatenate((output, rescale(tube, output)), axis=0)
    output = np.concatenate((output, rescale(img, output)), axis=0)
    return output, protrusion_length
