from core.LogInfor import LogInfor
from PyQt5.QtWidgets import QMessageBox
from windows import IdPassWindow
from .Session import Session

class IdPassSession(Session):
    def __init__(self) -> None:
        super().__init__()

        self.idPassWindow = IdPassWindow()

        self.idPassWindow.signals.closeWindow.connect(self.onCloseWindow)
        self.idPassWindow.signals.getIdPassCompleted.connect(self.onGetIdPassCompleted)

        self.userManager.signals.verifySuccessed.connect(self.onVerifySuccessed)
        self.userManager.signals.verifyFailed.connect(self.onVerifyFailed)
        self.userManager.signals.verifyError.connect(self.onError)


# Implement Session Interface
# ==========================================================================================
    # Start session
    # ======================================================================================
    def start(self):
        self.idPassWindow.start()

    # Restart session
    # ======================================================================================
    def restart(self):
        self.idPassWindow.restart()
# ==========================================================================================





# ==================================================================================================|
#   Begin: Handle signals of idPassWindow
# ==================================================================================================|


    # Handle getIdPassCompleted signal
    # ======================================================================================
    def onGetIdPassCompleted(self, infor):
        self.userManager.verify(mode="idpass", infor=infor)

    # Handle close window signal from idPasswindow
    # Emit sessionDone signal to system
    # ======================================================================================
    def onCloseWindow(self):
        self.signals.sessionDone.emit()


# ==================================================================================================|
#   End: Handle signals of idPassWindow
# ==================================================================================================|





# ==================================================================================================|
# Begin: Handle signals of userManager.verify()
# ==================================================================================================|


    # Handle verify successed
    # ======================================================================================
    def onVerifySuccessed(self, result):
        self.idPassWindow.hide()
        self.__notifyUser(QMessageBox.Information, "Welcome {}".format(result['label']))
        logInfor = LogInfor(mode='ID-Unlock', isValid='Valid', userId=result['label'])
        self.logManager.writeLog(logInfor)
        # unlock raspberry pi api
        self.idPassWindow.close()
    
    # Handle verify failed
    # ======================================================================================
    def onVerifyFailed(self, status):
        self.invalidCount += 1
        if self.invalidCount >= self.MAX_ALLOWED_TIMES:
            self.__notifyUser(QMessageBox.Critical, "You have unlocked more times than allowed!")
            logInfor = LogInfor(mode='ID-Unlock', isValid='Invalid', userId="Unknown")
            self.logManager.writeLog(logInfor)
            self.idPassWindow.close()
            self.signals.penalty.emit()
        else:
            retVal = self.__notifyUser(QMessageBox.Critical, f"Unlock failed, try again ?\nStatus: {status}", \
                QMessageBox.Ok | QMessageBox.Cancel)
            if retVal == QMessageBox.Ok:
                self.restart()
            else:
                self.idPassWindow.close()

    # Handle error
    # ======================================================================================
    def onError(self):
        self.__notifyUser(QMessageBox.Critical, "An error occured.")
        self.idPassWindow.close()


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