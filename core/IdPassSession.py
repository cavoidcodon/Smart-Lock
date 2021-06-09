from core.LogInfor import LogInfor
from PyQt5.QtWidgets import QMessageBox
from .ThreadWorker import ThreadWorker
from windows import IdPassWindow
from .Session import Session
import requests

class IdPassSession(Session):
    def __init__(self) -> None:
        super().__init__()

        self.idPassWindow = IdPassWindow()
        self.idPassUrl = 'http://localhost:5000/api/unlock/idpassword'

        self.idPassWindow.signals.closeWindow.connect(self.onCloseWindow)
        self.idPassWindow.signals.getIdPassCompleted.connect(self.onGetIdPassCompleted)


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
# --------------------------------------------------------------------------------------------------|
#   Begin: Handle signals of idPassWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Handle getIdPassCompleted signal
    # Get informations and send request to check
    # ======================================================================================
    def onGetIdPassCompleted(self, userId, password):
        # create a thread and send a request to server to check
        # analysis result and emit signal to system
        self.checkInforRequestThread = ThreadWorker(self.__checkInforRequest, userId, password)

        self.checkInforRequestThread.successed.connect(self.onCheckInforRequestSuccessed)
        self.checkInforRequestThread.httpError.connect(self.onHttpError)
        self.checkInforRequestThread.connectionError.connect(self.onConnectionError)
        self.checkInforRequestThread.requestError.connect(self.onConnectionError)

        self.checkInforRequestThread.start()

    # Handle close window signal from idPasswindow
    # Emit sessionDone signal to system
    # ======================================================================================
    def onCloseWindow(self):
        self.signals.sessionDone.emit()


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
#   End: Handle signals of idPassWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# Begin: Handle signals of checkInforRequestThread
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Handle request successed signal from checkInforRequestThread
    # ======================================================================================
    def onCheckInforRequestSuccessed(self, respone, status):
        self.idPassWindow.hide()
        
        if status == 200:
            if respone['existed'] and respone['status'] == 'Correct':
                self.__notifyUser(QMessageBox.Information, f"Welcome {respone['label']}.")
                logInfor = LogInfor(mode='IdPass-Unlock', isValid='Valid', userId=respone['label'])
                self.logManager.writeLog(logInfor)
                # unlock
                self.idPassWindow.close()
            else:
                self.invalidCount += 1
                if self.invalidCount >= self.MAX_ALLOWED_TIMES:
                    self.__notifyUser(QMessageBox.Critical, "You have unlocked more times than allowed!")
                    logInfor = LogInfor(mode='IdPass-Unlock', isValid='Invalid', userId=respone['label'])
                    self.logManager.writeLog(logInfor)
                    self.signals.penalty.emit()   
                    self.idPassWindow.close()            
                else:
                    if respone['existed'] and respone['status'] == 'Password Incorrect':
                        ret = self.__notifyUser(QMessageBox.Critical, "Password Incorrect, try again?", \
                            QMessageBox.Ok | QMessageBox.Cancel)
                    else:
                        ret = self.__notifyUser(QMessageBox.Critical, "UserId Incorrect, try agian?", \
                            QMessageBox.Ok | QMessageBox.Cancel)
                    
                    if ret == QMessageBox.Ok:
                        self.restart()
                    else:
                        self.idPassWindow.close()

    # Handle connection error when sending request
    # ======================================================================================
    def onConnectionError(self, str):
        self.__notifyUser(QMessageBox.Critical, f"{str}")
        self.idPassWindow.close()

    # Handle Http error when sending request
    # ======================================================================================
    def onHttpError(self, tupleVal):
        self.__notifyUser(QMessageBox.Critical, f"An error occurred: {tupleVal[0]}, {tupleVal[1]}")
        self.idPassWindow.close()


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

    # Function for check user informations request
    # ======================================================================================
    def __checkInforRequest(self, id, pwd):
        infor = {
            'user_id': id,
            'password': pwd
        }

        respone = requests.post(self.idPassUrl, params=infor)
        respone.raise_for_status()

        return respone
# =================================================================================================
# #################################################################################################
# =================================================================================================