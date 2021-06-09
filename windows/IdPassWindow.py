from core.Signals import Signals
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import QtGui
from ui import Ui_IdPassWindow
import re

class IdPassWindow(QMainWindow, Ui_IdPassWindow):
    def __init__(self, *args, **kwargs):
        super(IdPassWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.signals = Signals()
        self.userIdRegex = "\D[a-zA-Z0-9_]{5,15}"
        self.passwordRegex = "[0-9]{6,6}"
        
        self.cancelButton.clicked.connect(self.close)
        self.sendButton.clicked.connect(self.onSend)



    # Start window
    # ======================================================================================    
    def start(self):
        self.show()

    # restart window
    # ======================================================================================
    def restart(self):
        self.userIdLineEdit.clear()
        self.passwordLineEdit.clear()
        self.sendButton.setEnabled(True)
        self.cancelButton.setEnabled(True)
        self.__stopLoading()
        self.start()




# =====================================================================================================
# Handle signals of this windows
# =====================================================================================================
    # Handle sendButton clicked signal
    # =================================================================================================
    def onSend(self):
        userId = self.userIdLineEdit.text()
        password = self.passwordLineEdit.text()

        # Check user input
        if not re.search(self.userIdRegex, userId):
            self.__notifyUser(QMessageBox.Warning, "Your id must contains from 5 to 15 characters, "\
                "begin with a non-digit character, contains only alphabets, digits and underscore.")
            return
        
        if not re.search(self.passwordRegex, password):
            self.__notifyUser(QMessageBox.Warning, "Your password must contains 6 digit character.")
            return

        self.sendButton.setEnabled(False)
        self.cancelButton.setEnabled(False)
        self.signals.getIdPassCompleted.emit(userId, password)
        self.__loading()

    # Handle close signal
    # =================================================================================================
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        super().closeEvent(a0)
        self.signals.closeWindow.emit()




# =====================================================================================================
# Private functions
# =====================================================================================================
    # =================================================================================================
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str, buttons: QMessageBox.StandardButton=QMessageBox.Ok):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        msgBox.setStandardButtons(buttons)
        return msgBox.exec_()
    
    def __loading(self):
        self.label_4.setText('Checking ...')
        self.movie = QtGui.QMovie('/home/x6hdm/Code/client/resources/images/loading_3.gif')
        self.label_5.setMovie(self.movie)
        self.movie.start()

    def __stopLoading(self):
        self.movie.stop()
        self.label_4.clear()
        self.label_5.clear()

# =================================================================================================
# #################################################################################################
# =================================================================================================