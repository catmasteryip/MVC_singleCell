from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import time

class Worker(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)

    def process(self):
        # dummy worker process
        self.flag = False
        for n in range(0, 10):
            if self.flag:
                print( 'stop')
                break
            print( 'process {}'.format(n))
            time.sleep(0.5)
        self.finished.emit()

    finished = QtCore.pyqtSignal()

class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QtGui.QVBoxLayout(self)
        self.btn_run = QtGui.QPushButton('Run', self)
        self.layout.addWidget(self.btn_run)
        self.btn_cancel = QtGui.QPushButton('Cancel', self)
        self.layout.addWidget(self.btn_cancel)

        QtCore.QObject.connect(self.btn_run, QtCore.SIGNAL('clicked()'), self.run)
        QtCore.QObject.connect(self.btn_cancel, QtCore.SIGNAL('clicked()'), self.reject)

        QtCore.QObject.connect(self, QtCore.SIGNAL('rejected()'), self.stop_worker)

        self.show()
        self.raise_()

    def stop_worker(self):
        print( 'stop')
        self.worker.flag = True

    def run(self):
        # start the worker thread
        self.thread = QtCore.QThread(self)
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        QtCore.QObject.connect(self.thread, QtCore.SIGNAL('started()'), self.worker.process)
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL('finished()'), self.thread.quit)
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL('finished()'), self.worker.deleteLater)
        QtCore.QObject.connect(self.thread, QtCore.SIGNAL('finished()'), self.thread.deleteLater)
        self.thread.start()

def main():
    app = QtWidgets.QApplication(sys.argv)
    dlg = Dialog()
    ret = dlg.exec_()

if __name__ == '__main__':
    main()