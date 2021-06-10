from core.Signals import Signals
from PyQt5.QtWidgets import QWidget, QMessageBox
from ui import Ui_AdminForm
import re

class AdminForm(QWidget, Ui_AdminForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.signals = Signals()
        self.idRegex = "\D[a-zA-Z0-9_]{5,15}"
        self.passwordRegex = "[0-9]{6,6}"
        self.nameRegex = "^[a-zA-Z]+(([,. -][a-zA-Z ])?[a-zA-Z]*)*$"
        self.secretKeyRegex = "\D[a-zA-Z0-9_]{5,15}"

        self.pushButton.clicked.connect(self.onOk)
        self.pushButton_2.clicked.connect(self.close)

    def onOk(self):
        adminId = self.lineEdit.text()
        name = self.lineEdit_2.text()
        password = self.lineEdit_3.text()
        verifyPassword = self.lineEdit_4.text()
        secretKey = self.lineEdit_5.text()

        if not re.search(self.idRegex, adminId):
            self.__notifyUser(QMessageBox.Warning, "Your id must contains from 5 to 15 characters, begin with a non-digit character")
            return
        
        if not re.search(self.nameRegex, name):
            self.__notifyUser(QMessageBox.Warning, "Name invalid")
            return
        
        if not re.search(self.passwordRegex, password):
            self.__notifyUser(QMessageBox.Warning, "Your password must contains 6 digit character")
            return

        if verifyPassword != password:
            self.__notifyUser("Verify password incorrect")
            return
        
        if not re.search(self.secretKeyRegex, secretKey):
            self.__notifyUser(QMessageBox.Warning, "Secret Key must contains from 5 to 15 characters, begin with a non-digit character")
            return

        infor = {
            "user_id": adminId,
            "name": name,
            "password": password,
            "secret_key": secretKey
        }
        self.signals.takeInformationsCompleted.emit(infor)
    
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        return msgBox.exec_()