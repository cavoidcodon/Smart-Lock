from core.IdPassSession import IdPassSession
from PyQt5.QtCore import QTimer
from core.FaceRegSession import FaceRegSession
from core.AdminLoginSession import AdminLoginSession
from windows import MainWindow
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys

class System:
    def __init__(self):
        # Main window
        self.mainWindow = MainWindow()
        self.mainWindow.unlockButton.clicked.connect(self.onUnlock)
        self.mainWindow.loginAdminButton.clicked.connect(self.onLogin)

        # For penalty time
        self.isPenalty = False
        self.penaltyTimer = QTimer()
        self.penaltyTimer.setInterval(60000) # 1 minutes
        self.penaltyTimer.timeout.connect(self.onPenaltyTimerTimeout)

    # Start system
    def start(self):
        self.mainWindow.show()
    
    # Penalty time over
    def onPenaltyTimerTimeout(self):
        self.isPenalty = False
        self.penaltyTimer.stop()

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
    def onLogin(self):
        if self.isPenalty:
            self.__notifyUser(QMessageBox.Information, "You are in penalty time!")
            return

        self.mainWindow.setEnabled(False)
        self.session = AdminLoginSession()
        self.session.signals.sessionDone.connect(self.onSessionDone)
        self.session.signals.penalty.connect(self.onPenalty)
        self.session.start()
    # Slot for sessionDone signal
    def onSessionDone(self):
        self.mainWindow.setEnabled(True)
        # self.session = None # Delete session

    # Slot for onPenelty signal
    def onPenalty(self):
        self.isPenalty = True
        self.penaltyTimer.start()

    # Private function
    # Notify user with message box
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        return msgBox.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    system = System()
    system.start()
    sys.exit(app.exec_())
