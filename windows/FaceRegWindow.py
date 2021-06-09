from PyQt5.QtCore import QThread, QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow
from ui import Ui_FaceRegWindow
import cv2, numpy
from core.Signals import Signals

class FaceRegWindow(QMainWindow, Ui_FaceRegWindow):
    def __init__(self, timeout):
        super(FaceRegWindow, self).__init__()
        self.setupUi(self)

        self.loadingMovie = QtGui.QMovie('/home/x6hdm/Code/client/resources/images/loading_3.gif')
        self.inputImage = None
        self.signals = Signals()
        
        self.imageUpdateThread = UpdateImageThread()
        self.imageUpdateThread.imageUpdate.connect(self.updateImage)
        self.imageUpdateThread.cameraUnavailable.connect(lambda: self.signals.cameraUnavailable.emit())
        self.cancelButton.clicked.connect(self.close)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.countdown)
        self.limitedTime = timeout # count down in timeout seconds

    # Start window
    # ======================================================================================
    def start(self):
        self.counter = self.limitedTime
        self.isFirstTimeUpdateImage = True
        self.imageUpdateThread.start()
        self.show()

    # Restart window
    # ======================================================================================
    def restart(self):
        self.cancelButton.setEnabled(True)
        self.label.setText('System will get your face image in %d seconds'%self.limitedTime)
        self.__stopLoading()
        self.start()



# =====================================================================================================
# Handle signals of updateImage thread
# =====================================================================================================
    # Update image show in window every time timer tick
    # ======================================================================================
    def updateImage(self, pic: QImage, image: numpy.ndarray):
        self.label_2.setPixmap(QPixmap.fromImage(pic))
        self.inputImage = image
        if self.isFirstTimeUpdateImage:
            self.timer.start()
            self.isFirstTimeUpdateImage = False



# =====================================================================================================
# Handle signals of Timer thread
# =====================================================================================================
    # Handle timer tick signal
    # ======================================================================================
    def countdown(self):
        self.counter -= 1
        self.label.setText('System will get your face image in %d seconds'%self.counter)
        if self.counter == 0:
            self.timer.stop()
            try:
                self.imageUpdateThread.stop()
            except:
                pass
            self.cancelButton.setEnabled(False)
            # Emit getFaceCompleted signal when timeout
            self.signals.getFaceCompeleted.emit(self.inputImage)
            self.__loading()





# =====================================================================================================
# Handle signals of this window
# =====================================================================================================
    # Handle close signal
    # ======================================================================================
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        try:
            self.imageUpdateThread.stop()
        except:
            pass
        self.timer.stop()
        super().closeEvent(a0)
        self.signals.closeWindow.emit()





# =====================================================================================================
# Private functions
# =====================================================================================================
    # ======================================================================================
    def __loading(self):
        self.label_3.setMovie(self.loadingMovie)
        self.loadingMovie.start()
        self.label.setText('Checking your face ...')
    
    def __stopLoading(self):
        self.loadingMovie.stop()
        self.label_3.clear()
        self.label.clear()
    # ======================================================================================





# Update image thread
# ======================================================================================
class UpdateImageThread(QThread):
    imageUpdate = pyqtSignal(QImage, numpy.ndarray)
    cameraUnavailable = pyqtSignal()

    def run(self):
        self.threadActive = True
        self.capture = cv2.VideoCapture(0)
        # Check for camera available
        if not self.capture.isOpened():
            self.cameraUnavailable.emit()

        while self.threadActive:
            ret, frame = self.capture.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flippedImage = cv2.flip(image, 1)
                convertToQtFormat = QImage(flippedImage.data, flippedImage.shape[1], flippedImage.shape[0], QImage.Format_RGB888)
                pic = convertToQtFormat.scaled(380, 290, Qt.KeepAspectRatio)
                self.imageUpdate.emit(pic, image)
        
        self.capture.release()
    
    def stop(self):
        self.threadActive = False

# =================================================================================================
# #################################################################################################
# =================================================================================================