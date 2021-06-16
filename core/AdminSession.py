from core.UpdateManager import UpdateManager
from core.UserManager import UserManager
from core.LogInfor import LogInfor
import numpy, io, requests, json
from core.Signals import Signals
from PyQt5.QtWidgets import QMessageBox
from PIL import Image
from PIL.Image import fromarray
from .ThreadWorker import ThreadWorker
from .Session import Session
from windows import PasswordForm, FaceRegWindow, AdminWindow


class AdminSession(Session):
    def __init__(self) -> None:
        super().__init__()

        self.signals = Signals()

        self.passwordWindow = PasswordForm()
        self.faceRegWindow = FaceRegWindow(timeout=5)

        self.updateManager = UpdateManager()
        self.updateManager.signals.updateSuccessed.connect(lambda: \
            self.signals.updateSuccessed.emit())
        self.updateManager.signals.updateFailed.connect(lambda: \
            self.signals.updateFailed.emit())
        self.updateManager.signals.updateError.connect(lambda: \
            self.signals.updateError.emit())
        
        self.updateManager.signals.checkUpdateSuccessed.connect(lambda resp: \
            self.signals.checkUpdateSuccessed.emit(resp))
        self.updateManager.signals.checkUpdateError.connect(lambda: \
            self.signals.checkUpdateError.emit())

        # Connect window signals to session's slots
        self.faceRegWindow.signals.closeWindow.connect(self.onCloseWindow)
        self.faceRegWindow.signals.getFaceCompeleted.connect(self.onGetFaceCompleted)
        self.faceRegWindow.signals.cameraUnavailable.connect(self.onCameraUnavailable)

        self.passwordWindow.signals.closeWindow.connect(self.onCloseWindow)
        self.passwordWindow.signals.getPassCompleted.connect(self.onGetPassCompleted)

        self.userManager.signals.verifySuccessed.connect(self.onVerifySuccessed)
        self.userManager.signals.verifyFailed.connect(self.onVerifyFailed)
        self.userManager.signals.verifyError.connect(self.onVerifyError)

        self.userManager.signals.changeUserInforSuccessed.connect(lambda: \
            self.signals.changeUserInforSuccessed.emit())
        self.userManager.signals.changeUserInforFailed.connect(lambda: \
            self.signals.changeUserInforFailed.emit())
        self.userManager.signals.changeUserInforError.connect(lambda: \
            self.signals.changeUserInforError.emit())

        self.userManager.signals.delUserSuccessed.connect(lambda: self.signals.delUserSuccessed.emit())
        self.userManager.signals.delUserFailed.connect(lambda: self.signals.delUserFailed.emit())
        self.userManager.signals.delUserError.connect(lambda: self.signals.delUserError.emit())

        self.userManager.signals.addUserSuccessed.connect(lambda: \
            self.signals.addUserSuccessed.emit())
        self.userManager.signals.addUserFailed.connect(lambda: self.signals.addUserFailed.emit())
        self.userManager.signals.addUserError.connect(lambda: self.signals.addUserError.emit())

        self.logManager.signals.queryLogSuccessed.connect(lambda res: self.signals.queryLogSuccessed.emit(res))
        self.logManager.signals.queryLogFailed.connect(lambda: self.signals.queryLogFailed.emit())
        self.logManager.signals.queryLogError.connect(lambda: self.signals.queryLogError.emit())



# Implement Session Interface
# ==========================================================================================
    # Start session
    # ==================================================================
    def start(self):
        self.faceRegWindow.start()

    # Restart session
    # ==================================================================
    def restart(self):
        self.passwordWindow.hide()
        self.passwordWindow.clearContent()
        self.faceRegWindow.restart()
# =========================================================================================





# ==================================================================================================|
#   Begin: Handle signals of faceRegWindow
# ==================================================================================================|


    # Handle getFaceCompleted signal from faceRegWindow
    # ======================================================================================
    def onGetFaceCompleted(self, face):
        self.faceImg = face
        self.faceRegWindow.hide()
        self.passwordWindow.show()

    # Handle camera unavailable case
    # ======================================================================================
    def onCameraUnavailable(self):
        self.__notifyUser(QMessageBox.Critical, "Can not open camera.")
        self.faceRegWindow.close()
    
    # Handle close window signal from faceRegWindow
    # Emit sessionDone signal to system
    # ======================================================================================
    def onCloseWindow(self):
        self.signals.sessionDone.emit()
# ==================================================================================================|
#   End: Handle signals of faceRegWindow
# ==================================================================================================|





# ==================================================================================================|
#   Begin: Handle signals of passwordForm
# ==================================================================================================|


    # Handle getPassCompleted signal from passwordForm
    # ======================================================================================
    def onGetPassCompleted(self, pwd):
        self.userManager.verify(mode='admin-login', faceImage=self.faceImg, password=pwd)

    # Handle request successed signal from loginRequest
    # ======================================================================================
    def onVerifySuccessed(self, result):
        self.passwordWindow.hide()
        logInfor = LogInfor(mode='Login', isValid='Valid', userId=result['label'], image=self.faceImg)
        self.logManager.writeLog(logInfor)

        if result["isNeedUpdate"]:
            self.__notifyUser(QMessageBox.Information, "System need to update. Go to updatetab"\
                " in main window to see system status and update") 
        
        self.adminWindow = AdminWindow(users=result['data']['users'], logs=result['data']['logs'], updateLogs=result['data']['update'])
        self.adminWindow.signals.closeWindow.connect(self.onCloseWindow)

            # Connect signals from admin window:
            #   + deleteUser signal
            #   + changeUserInfor signal
        self.adminWindow.signals.deleteUser.connect(self.onDeleteUser)
        self.signals.delUserSuccessed.connect(self.adminWindow.onDelUserSuccessed)
        self.signals.delUserFailed.connect(self.adminWindow.onDelUserFailed)
        self.signals.delUserError.connect(self.adminWindow.onDelUserError)

        self.adminWindow.signals.changeUserInfor.connect(self.onChangeUserInfor)
        self.signals.changeUserInforSuccessed.connect(self.adminWindow.onChangeUserInforSuccessed)
        self.signals.changeUserInforFailed.connect(self.adminWindow.onChangeUserInforFailed)
        self.signals.changeUserInforError.connect(self.adminWindow.onChangeUserInforFailed)

        self.adminWindow.signals.checkFace.connect(self.onCheckFace)
        self.signals.checkFaceSuccessed.connect(self.adminWindow.onCheckFaceSuccessed)
        self.signals.checkFaceFailed.connect(self.adminWindow.onCheckFaceFailed)
        self.signals.checkFaceError.connect(self.adminWindow.onCheckFaceError)

        self.adminWindow.signals.addUser.connect(self.onAddUser)
        self.signals.addUserSuccessed.connect(self.adminWindow.onAddUserSuccessed)
        self.signals.addUserFailed.connect(self.adminWindow.onAddUserFailed)
        self.signals.addUserError.connect(self.adminWindow.onAddUserFailed)

        self.adminWindow.signals.queryLog.connect(self.onQueryLog)
        self.signals.queryLogSuccessed.connect(self.adminWindow.onQueryLogSuccessed)
        self.signals.queryLogFailed.connect(self.adminWindow.onQueryLogFailed)
        self.signals.queryLogError.connect(self.adminWindow.onQueryLogFailed)

        self.adminWindow.signals.update.connect(self.onUpdate)
        self.signals.updateSuccessed.connect(self.adminWindow.onUpdateSuccessed)
        self.signals.updateFailed.connect(self.adminWindow.onUpdateFailed)
        self.signals.updateError.connect(self.adminWindow.onUpdateError)

        self.adminWindow.signals.checkUpdate.connect(self.onCheckUpdate)
        self.signals.checkUpdateError.connect(self.adminWindow.onCheckUpdateError)
        self.signals.checkUpdateSuccessed.connect(self.adminWindow.onCheckUpdateSuccessed) 
            
        self.adminWindow.show()
    
    def onVerifyFailed(self, status):
        self.invalidCount += 1
        if self.invalidCount >= self.MAX_ALLOWED_TIMES:
            self.__notifyUser(QMessageBox.Critical, "You have logged in more times than allowed!")
            logInfor = LogInfor(mode='Login', isValid='Invalid', userId="Unknown", image=self.faceImg)
            self.logManager.writeLog(logInfor)
            self.passwordWindow.close()
        else:
            ret = self.__notifyUser(QMessageBox.Critical, "Login falied, try again ?", \
            QMessageBox.Ok | QMessageBox.Cancel)
            if ret == QMessageBox.Ok:
                self.restart()
            else:
                self.passwordWindow.close()

    def onVerifyError(self):
        self.__notifyUser(QMessageBox.Critical, "An error occured.")
        self.passwordWindow.close()
# ==================================================================================================|
#   End: Handle signals of passwordForm
# ==================================================================================================|





# ==================================================================================================|
# Begin: Handle signal deleteUser of adminWindow
# ==================================================================================================|

    def onDeleteUser(self, userId):
        self.userManager.delete(userId)
# ==================================================================================================|
# End: Handle signal deleteUser of adminWindow
# ==================================================================================================|





# ==================================================================================================|
# Begin: Handle signal changeUserInfor of adminWindow
# ==================================================================================================|

    def onChangeUserInfor(self, infor):
        self.userManager.changeInfor(infor)
# ==================================================================================================|
# End: Handle signal changeUserInfor of adminWindow
# ==================================================================================================|





# ==================================================================================================|
# Begin: Handle signal addUser of adminWindow
# ==================================================================================================|

    def onCheckFace(self, face):
        self.userManager_1 = UserManager()
        self.userManager_1.verify(mode='face-regconition', faceImage=face)

        self.userManager_1.signals.verifySuccessed.connect(lambda resp: self.signals.checkFaceSuccessed.emit())
        self.userManager_1.signals.verifyFailed.connect(lambda status: self.signals.checkFaceFailed.emit())
        self.userManager_1.signals.noFaceDectect.connect(lambda: self.signals.checkFaceError.emit())
        self.userManager_1.signals.verifyError.connect(lambda: self.signals.checkFaceError.emit())
    
    def onAddUser(self, infor, listFace):
        self.userManager.add(infor, listFace)
# ==================================================================================================|
# End: Handle signal addUser of adminWindow
# ==================================================================================================|





# ==================================================================================================|
# Begin: Handle signal queryLog of adminWindow
# ==================================================================================================|

    # ==============================================================================================
    def onQueryLog(self, constraints):
        self.logManager.query(constraints)
# ==================================================================================================|
# End: Handle signal queryLog of adminWindow
# ==================================================================================================|



# ==================================================================================================|
# Begin: Handle signal update of adminWindow
# ==================================================================================================|
    def onUpdate(self):
        self.updateManager.update()

    def onCheckUpdate(self):
        self.updateManager.checkUpdate()
# ==================================================================================================|
# End: Handle signal update of adminWindow
# ==================================================================================================|



# Private function
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