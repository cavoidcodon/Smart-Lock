import cv2
from core.Signals import Signals
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox, QWidget
from ui import Ui_FaceForm
from .FaceRegWindow import UpdateImageThread
import re, numpy, base64

class FaceForm(QWidget, Ui_FaceForm):
    def __init__(self, mode):
        super(FaceForm, self).__init__()
        self.setupUi(self)

        self.currentImage = None
        self.signals = Signals()
        self.imageUpdateThread = UpdateImageThread()
        self.imageUpdateThread.imageUpdate.connect(self.updateImage)
        self.imageUpdateThread.cameraUnavailable.connect(self.onCameraUnavailable)
        self.takedFace = []
        self.mode = mode

        if mode == 'checking':
            self.takeButton.setText('Check')
            self.takeButton.clicked.connect(self.onCheckFaceImage)
        else:
            self.takeButton.setText('Take')
            self.label_2.setText("At least 10 face images: ")
            self.takedImageNumb = 0
            self.label_3.setText(str(self.takedImageNumb))
            self.takeButton.clicked.connect(self.onTakeFaceImage)

        self.cancelButton.clicked.connect(self.close)

    def onTakeFaceImage(self):
        b64Str = self._image2b64Str(self.currentImage)
        self.takedFace.append(b64Str)
        self.takedImageNumb += 1
        self.label_3.setText(str(self.takedImageNumb))
        if self.takedImageNumb >= 10:
            self.signals.takeFaceCompeleted.emit(self.takedFace)
            self.imageUpdateThread.stop()
            self.__loading()

    def _image2b64Str(self, image: numpy.ndarray) -> str:
        retval, buffer = cv2.imencode('.jpg', image)
        picStr = base64.b64encode(buffer)
        return picStr.decode()
    
    def onCheckFaceImage(self):
        self.__loading()
        self.signals.checkFace.emit(self.currentImage)

    def start(self):
        self.imageUpdateThread.start()
        self.show()
    
    def onCameraUnavailable(self):
        self.__notifyUser(QMessageBox.Critical, "Camera Unavailable.")
        self.close()

    def updateImage(self, pic: QtGui.QImage, image: numpy.ndarray):
        self.label.setPixmap(QtGui.QPixmap.fromImage(pic))
        self.currentImage = image

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.imageUpdateThread.stop()
        super().closeEvent(a0)
    
    def __loading(self):
        if self.mode == 'checking':
            self.label_2.setText('Checking ...')
        self.movie = QtGui.QMovie('/home/x6hdm/Code/client/resources/images/loading_3.gif')
        self.label_3.setMovie(self.movie)
        self.movie.start()

    def __stopLoading(self):
        self.movie.stop()
        self.label_3.clear()
        self.label_2.clear()
    
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        return msgBox.exec_()
