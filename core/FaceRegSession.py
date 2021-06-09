from PyQt5.QtWidgets import QMessageBox
from requests.models import Response
from .ThreadWorker import ThreadWorker
from .Session import Session
from windows import FaceRegWindow
from PIL import Image
from PIL.Image import fromarray
import requests, io, numpy
from .LogInfor import LogInfor

class FaceRegSession(Session):

    def __init__(self) -> None:
        super().__init__()
        self.faceRegUrl = 'http://localhost:5000/api/unlock/face-recognition'
        self.faceRegWindow = FaceRegWindow(timeout=5)
        self.faceImage = None

        self.faceRegWindow.signals.cameraUnavailable.connect(self.onCameraUnavailable)
        self.faceRegWindow.signals.getFaceCompeleted.connect(self.onGetFaceCompleted)
        self.faceRegWindow.signals.closeWindow.connect(self.onCloseWindow)



# Implement Session Interface
# ==========================================================================================
    # Start session
    # ======================================================================================
    def start(self):
        self.faceRegWindow.start()

    # Restart session
    # ======================================================================================
    def restart(self):
        self.faceRegWindow.restart()
# ==========================================================================================





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
#   Begin: Handle signals of faceRegWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Handle camera unavailable case
    # ======================================================================================
    def onCameraUnavailable(self):
        self.__notifyUser(QMessageBox.Critical, "Can not open camera.")
        self.faceRegWindow.close()

    # Handle getFaceCompleted signal from faceRegWindow
    # Get face image and request to check
    # ======================================================================================
    def onGetFaceCompleted(self, face):
        # Save face image for write log
        self.faceImage = face

        self.checkFaceRequestThread = ThreadWorker(self.__checkFaceRequest, face)

        self.checkFaceRequestThread.successed.connect(self.onCheckFaceRequestSuccessed)
        self.checkFaceRequestThread.httpError.connect(self.onHttpError)
        self.checkFaceRequestThread.connectionError.connect(self.onConnectionError)
        self.checkFaceRequestThread.requestError.connect(self.onConnectionError)

        self.checkFaceRequestThread.start()

    # Handle close window signal from faceRegWindow
    # Emit sessionDone signal to system
    # ======================================================================================
    def onCloseWindow(self):
        self.signals.sessionDone.emit()


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
#   End: Handle signals of faceRegWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# Begin: Handle signals of checkFaceRequestThread
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Handle request successed signal from checkFaceRequestThread
    # ======================================================================================
    def onCheckFaceRequestSuccessed(self, result, status):
        self.faceRegWindow.hide()
        if status == 200:
            if result['existed']:
                self.__notifyUser(QMessageBox.Information, "Welcome {}".format(result['label']))
                logInfor = LogInfor(mode='Face-Unlock', isValid='Valid', image=self.faceImage, userId=result['label'])
                self.logManager.writeLog(logInfor)
                # unlock raspberry pi api
                self.faceRegWindow.close()
            elif result['status'] == 'No Face':
                self.__notifyUser(QMessageBox.Critical, "No face detected !")
                self.faceRegWindow.close()
            else:
                self.invalidCount += 1
                if self.invalidCount >= self.MAX_ALLOWED_TIMES:
                    self.__notifyUser(QMessageBox.Critical, "You have unlocked more times than allowed!")
                    logInfor = LogInfor(mode='Face-Unlock', isValid='Invalid', image=self.faceImage, userId=result['label'])
                    self.logManager.writeLog(logInfor)
                    self.faceRegWindow.close()
                    self.signals.penalty.emit()
                else:
                    retVal = self.__notifyUser(QMessageBox.Critical, "Unlock failed, try again ?", QMessageBox.Ok | QMessageBox.Cancel)
                    if retVal == QMessageBox.Ok:
                        self.restart()
                    else:
                        self.faceRegWindow.close()
    
    # Handle connection error when sending request
    # ======================================================================================
    def onConnectionError(self, str):
        self.__notifyUser(QMessageBox.Critical, f"{str}")
        self.faceRegWindow.close()

    # Handle Http error when sending request
    # ======================================================================================
    def onHttpError(self, tupleVal):
        self.__notifyUser(QMessageBox.Critical, f"An error occurred: {tupleVal[0]}, {tupleVal[1]}")
        self.faceRegWindow.close()


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# End: Handle signals of checkFaceRequestThread
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|
    




# Private function
# ======================================================================================
    # ======================================================================================
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str, buttons: QMessageBox.StandardButton=QMessageBox.Ok):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        msgBox.setStandardButtons(buttons)
        return msgBox.exec_()

    # Function for check face request
    # ======================================================================================
    def __checkFaceRequest(self, faceImage: numpy.ndarray) -> Response:
        image = Image.fromarray(faceImage)
        buff = io.BytesIO()
        image.save(buff, format='JPEG')
        bytesImage = buff.getvalue()
        
        obj = {'image': bytesImage}
        resp = requests.post(self.faceRegUrl, files = obj)
        resp.raise_for_status()

        return resp
# =================================================================================================
# #################################################################################################
# =================================================================================================