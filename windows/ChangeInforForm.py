from core.Signals import Signals
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox, QWidget
from ui import Ui_ChangeInforForm
import re

class ChangeInforForm(QWidget, Ui_ChangeInforForm):
    def __init__(self, userId, role):
        super(ChangeInforForm, self).__init__()
        self.setupUi(self)

        self.userId = userId
        self.role = role
        self.signals = Signals()
        self.passwordRegex = "[0-9]{6,6}"

        self.label_5.setText(userId)
        if role == 'Admin':
            self.comboBox.setCurrentIndex(0)
            self.comboBox.setEnabled(False)
        else:
            self.comboBox.setCurrentIndex(1)

        self.pushButton_2.clicked.connect(self.onChangeUserInfor)
        self.pushButton.clicked.connect(self.close)
    

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        super().closeEvent(a0)
        self.signals.closeWindow.emit()

    # Handle changeUserInfor button clicked
    # ================================================================================   
    def onChangeUserInfor(self):
        password = self.lineEdit_2.text()
        verifyPass = self.lineEdit.text()
        role = self.comboBox.currentText()

        if not password and not verifyPass:
            if role == self.role:
                self.close()
                self.__notifyUser(QMessageBox.Information, "Nothing change")
                return
            elif self.role == 'Normal' and role == 'Admin':
                ret = self.__notifyUser(QMessageBox.Warning, "Change this user's role to admin will "\
                    "change role of current addmin " \
                    "to 'Normal'. Do you want to continue?", QMessageBox.Ok | QMessageBox.Cancel)
                
                if ret == QMessageBox.Ok:
                    self.signals.getChangeInforCompleted.emit((self.userId, password, role))
                    return
                else:
                    return

        if not re.search(self.passwordRegex, password):
            self.__notifyUser(QMessageBox.Warning, "Your password must contains 6 digit character")
            return

        if verifyPass != password:
            self.__notifyUser(QMessageBox.Warning, "Verify password not correct")
            return
        
        if self.role == 'Normal' and role == 'Admin':
                ret = self.__notifyUser(QMessageBox.Warning, "Change this user's role to admin will "\
                    "change role of current addmin " \
                    "to 'Normal'. Do you want to continue?", QMessageBox.Ok | QMessageBox.Cancel)
                
                if ret == QMessageBox.Ok:
                    self.signals.getChangeInforCompleted.emit((self.userId, password, role))
                    return
                else:
                    return
        self.signals.getChangeInforCompleted.emit((self.userId, password, role))
        self.__loading()

    # Private function
    # ===================================================================================
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str, buttons: QMessageBox.StandardButton=QMessageBox.Ok):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        msgBox.setStandardButtons(buttons)
        return msgBox.exec_()

    def __loading(self):
        self.movie = QtGui.QMovie('/home/x6hdm/Code/client/resources/images/loading_3.gif')
        self.label_7.setMovie(self.movie)
        self.movie.start()
        self.label_6.setText('Changing...')

    def __stopLoading(self):
        self.movie.stop()
        self.label_6.clear()
        self.label_7.clear()