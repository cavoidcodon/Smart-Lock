from PyQt5.QtWidgets import QMessageBox
from .Session import Session
from windows import FaceRegWindow
from .LogInfor import LogInfor

class FaceRegSession(Session):

    def __init__(self) -> None:
        super().__init__()

        self.faceRegWindow = FaceRegWindow(timeout=5)
        self.faceImage = None

        self.faceRegWindow.signals.cameraUnavailable.connect(self.onCameraUnavailable)
        self.faceRegWindow.signals.getFaceCompeleted.connect(self.onGetFaceCompleted)
        self.faceRegWindow.signals.closeWindow.connect(self.onCloseWindow)

        self.userManager.signals.verifySuccessed.connect(self.onVerifySuccessed)
        self.userManager.signals.verifyFailed.connect(self.onVerifyFailed)
        self.userManager.signals.noFaceDectect.connect(self.onNoFaceDetect)
        self.userManager.signals.verifyError.connect(self.onError)



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
#   Begin: Handle signals of faceRegWindow
# ==================================================================================================|


    # Handle camera unavailable case
    # ======================================================================================
    def onCameraUnavailable(self):
        self.__notifyUser(QMessageBox.Critical, "Can not open camera.")
        self.faceRegWindow.close()

    # Handle getFaceCompleted signal from faceRegWindow
    # ======================================================================================
    def onGetFaceCompleted(self, face):
        self.faceImage = face
        self.userManager.verify(mode='face-regconition', faceImage=self.faceImage)
        

    # Handle close window signal from faceRegWindow
    # Emit sessionDone signal to system
    # ======================================================================================
    def onCloseWindow(self):
        self.signals.sessionDone.emit()


# ==================================================================================================|
#   End: Handle signals of faceRegWindow
# ==================================================================================================|





# ==================================================================================================|
# Begin: Handle signals of userManager.verify()
# ==================================================================================================|


    # Handle verify successed
    # ======================================================================================
    def onVerifySuccessed(self, result):
        self.faceRegWindow.hide()
        self.__notifyUser(QMessageBox.Information, "Welcome {}".format(result['label']))
        logInfor = LogInfor(mode='Face-Unlock', isValid='Valid', image=self.faceImage, userId=result['label'])
        self.logManager.writeLog(logInfor)
        # unlock raspberry pi api
        self.faceRegWindow.close()
    
    # Handle no face detect
    # ======================================================================================
    def onNoFaceDetect(self):
        self.__notifyUser(QMessageBox.Critical, "No face detected !")
        self.faceRegWindow.close()
    
    # Handle verify failed
    # ======================================================================================
    def onVerifyFailed(self, status):
        self.invalidCount += 1
        if self.invalidCount >= self.MAX_ALLOWED_TIMES:
            self.__notifyUser(QMessageBox.Critical, "You have unlocked more times than allowed!")
            logInfor = LogInfor(mode='Face-Unlock', isValid='Invalid', image=self.faceImage, userId="Unknown")
            self.logManager.writeLog(logInfor)
            self.faceRegWindow.close()
            self.signals.penalty.emit()
        else:
            retVal = self.__notifyUser(QMessageBox.Critical, f"Unlock failed, try again ?\nStatus: {status}", \
                QMessageBox.Ok | QMessageBox.Cancel)
            if retVal == QMessageBox.Ok:
                self.restart()
            else:
                self.faceRegWindow.close()

    # Handle error
    # ====================================================================================== 
    def onError(self):
        self.__notifyUser(QMessageBox.Critical, "An error occured.")
        self.faceRegWindow.close()


# ==================================================================================================|
# End: Handle signals of userManager.verify()
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

# =================================================================================================
# #################################################################################################
# =================================================================================================