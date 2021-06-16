from core.UpdateManager import UpdateManager
from windows.SecretKeyForm import SecretKeyForm
from core.IdPassSession import IdPassSession
from PyQt5.QtCore import QTimer
from core.FaceRegSession import FaceRegSession
from core.AdminSession import AdminSession
from windows import MainWindow, AdminForm, FaceForm
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys
from core.ThreadWorker import ThreadWorker
from core.UserManager import UserManager
import Setings

class System:
    def __init__(self):
        # Main window
        self.mainWindow = MainWindow()

        # For penalty time
        self.userManager = UserManager()
        self.userManager.signals.notEmpty.connect(self.onSystemNotEmpty)
        self.userManager.signals.empty.connect(self.onSystemEmpty)
        self.userManager.signals.checkError.connect(self.onError)
        self.updateManager = UpdateManager()
        self.updateManager.signals.resetSuccessed.connect(self.onResetSuccessed)
        self.updateManager.signals.resetError.connect(self.onResetError)
        self.isPenalty = False
        self.penaltyTimer = QTimer()
        self.penaltyTimer.setInterval(60000) # 1 minutes
        self.penaltyTimer.timeout.connect(self.onPenaltyTimerTimeout)

# Start system
# ======================================================================================
# ======================================================================================
    def start(self):
        self.userManager.checkSystem()
    
    def onSystemNotEmpty(self):
        self.mainWindow.unlockButton.clicked.connect(self.onUnlock)
        self.mainWindow.loginAdminButton.clicked.connect(self.onLogin)
        self.mainWindow.pushButton_2.clicked.connect(self.onReset)
        self.mainWindow.show()

    def onSystemEmpty(self):
        self.mainWindow.unlockButton.clicked.connect(self.onBegin)
        self.mainWindow.loginAdminButton.clicked.connect(self.onBegin)
        self.mainWindow.show()
    
    def onError(self):
        self.__notifyUser(QMessageBox.Critical, "An error occurred.")
        self.mainWindow.close()

# ======================================================================================
# ======================================================================================

# Handle reset system
# ======================================================================================
# ======================================================================================    
    def onReset(self):
        self.secretKeyForm = SecretKeyForm()
        self.secretKeyForm.signals.resetSystem.connect(self.updateManager.reset)
        self.secretKeyForm.show()
    
    def onResetSuccessed(self):
        self.secretKeyForm.close()
        self.__notifyUser(QMessageBox.Information, "Reset successed.")
        self.mainWindow.unlockButton.clicked.disconnect()
        self.mainWindow.loginAdminButton.clicked.disconnect()
        self.mainWindow.pushButton_2.clicked.disconnect()
        self.start()
    
    def onResetError(self):
        self.secretKeyForm.close()
        self.__notifyUser(QMessageBox.Critical, "Reset Error.")

# ======================================================================================
# ======================================================================================


# Handle when no user in system
# ======================================================================================
# ======================================================================================
    def onBegin(self):
        retVal = self.__notifyUser(QMessageBox.Information, \
            "You must add first user. By default, first user is Admin.", QMessageBox.Ok | QMessageBox.Cancel)
        if retVal == QMessageBox.Ok:
            self.mainWindow.setEnabled(False)
            self.adminForm = AdminForm()
            self.adminForm.signals.takeInformationsCompleted.connect(self.onTakeInforCompleted)
            self.adminForm.show()
    
    def onTakeInforCompleted(self, infor):
        self.adminForm.close()
        self.addingAdminInfor = infor
        self.faceForm = FaceForm(mode='taking')
        self.faceForm.signals.cameraUnavailable.connect(self.onCameraUnavailable)
        self.faceForm.signals.takeFaceCompeleted.connect(self.onTakeFaceCompleted)
        self.faceForm.start()
    
    def onCameraUnavailable(self):
        self.__notifyUser(QMessageBox.Critical, "Camera unavailable.")
        self.faceForm.close()
        self.mainWindow.setEnabled(True)

    def onTakeFaceCompleted(self, faces):
        self.addingAdminFaces = faces
        self.userManager.addAdmin(self.addingAdminInfor, self.addingAdminFaces)
        self.userManager.signals.addAdminSuccessed.connect(self.onAddAdminSuccessed)
        self.userManager.signals.addAdminFailed.connect(self.onAddAdminFailed)

    def onAddAdminFailed(self):
        self.__notifyUser(QMessageBox.Critical, "Add Admin failed.")
        self.faceForm.close()
        self.mainWindow.setEnabled(True)
    
    def onAddAdminSuccessed(self):
        self.__notifyUser(QMessageBox.Information, "Add admin successful.")
        self.faceForm.close()
        self.mainWindow.setEnabled(True)
        self.mainWindow.unlockButton.clicked.disconnect()
        self.mainWindow.loginAdminButton.clicked.disconnect()
        self.mainWindow.unlockButton.clicked.connect(self.onUnlock)
        self.mainWindow.loginAdminButton.clicked.connect(self.onLogin)
        self.mainWindow.pushButton_2.clicked.connect(self.onReset)

# ======================================================================================
# ======================================================================================


# Handle when system has users
# ======================================================================================
# ======================================================================================
    # Slot for unlockButton clicked signal
    def onUnlock(self):
        if self.isPenalty:
            self.__notifyUser(QMessageBox.Information, "You are in penalty time!")
            return

        # Type of unlock mode
        unlockType = self.mainWindow.unlockOptionsComboBox.currentText()
        self.mainWindow.setEnabled(False)
        if unlockType == 'Face Regconition':
            self.session = FaceRegSession()
        else:
            self.session = IdPassSession()
        
        self.session.signals.sessionDone.connect(self.onSessionDone)
        self.session.signals.penalty.connect(self.onPenalty)
        self.session.start()

    # Slot for loginButton clicked signal
    # ======================================================================================
    def onLogin(self):
        if self.isPenalty:
            self.__notifyUser(QMessageBox.Information, "You are in penalty time!")
            return

        self.mainWindow.setEnabled(False)
        self.session = AdminSession()
        self.session.signals.sessionDone.connect(self.onSessionDone)
        self.session.signals.penalty.connect(self.onPenalty)
        self.session.start()

    # Slot for sessionDone signal
    # ======================================================================================
    def onSessionDone(self):
        self.mainWindow.setEnabled(True)
        # self.session = None # Delete session

    # Penalty time over
    # ======================================================================================
    def onPenaltyTimerTimeout(self):
        self.isPenalty = False
        self.penaltyTimer.stop()

    # Slot for onPenelty signal
    # ======================================================================================
    def onPenalty(self):
        self.isPenalty = True
        self.penaltyTimer.start()

# ======================================================================================
# ======================================================================================


# Private function
# ======================================================================================
    # Notify user with message box
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str, buttons: QMessageBox.StandardButton=QMessageBox.Ok):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        msgBox.setStandardButtons(buttons)
        return msgBox.exec_()

# ======================================================================================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Setings.initialize(sys.argv[1], sys.argv[2])
    system = System()
    system.start()
    sys.exit(app.exec_())
