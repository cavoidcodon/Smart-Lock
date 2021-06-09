from core.Signals import Signals
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox, QWidget
from ui import Ui_PasswordForm
import re

class PasswordForm(QWidget, Ui_PasswordForm):
    def __init__(self, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.sendButton.clicked.connect(self.onSend)
        self.cancelButton.clicked.connect(self.close)
        self.passwordRegex = "[0-9]{6,6}"
        self.signals = Signals()

    # Start window
    # ======================================================================================
    def start(self):
        self.show()

    # clear content of this window
    # ======================================================================================
    def clearContent(self):
        self.passwordLineEdit.clear()
        self.sendButton.setEnabled(True)
        self.__stopLoading()





# =====================================================================================================
# Handle signals of this windows
# =====================================================================================================
    # Handle sendButton clicked signal
    # =================================================================================================
    def onSend(self):
        password = self.passwordLineEdit.text()

        if not re.search(self.passwordRegex, password):
            self.__notifyUser(QMessageBox.Warning, "Your password must contains 6 digit character")
            return

        self.sendButton.setEnabled(False)
        self.__loading()
        self.signals.getPassCompleted.emit(password)

    # Handle close window signal
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
        self.movie = QtGui.QMovie('/home/x6hdm/Code/client/resources/images/loading_3.gif')
        self.label_2.setMovie(self.movie)
        self.movie.start()

    def __stopLoading(self):
        self.movie.stop()
        self.label_2.clear()
# =================================================================================================
# #################################################################################################
# =================================================================================================
