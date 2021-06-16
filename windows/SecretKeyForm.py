from core.Signals import Signals
from PyQt5.QtWidgets import QMessageBox, QWidget
from ui import Ui_SecretKeyForm
import re

class SecretKeyForm(QWidget, Ui_SecretKeyForm):
    def __init__(self, *args, **kwargs):
        super(SecretKeyForm, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.signals = Signals()

        self.secretKeyRegex = "\D[a-zA-Z0-9_]{5,15}"
        self.pushButton.clicked.connect(self.onReset)
        self.pushButton_2.clicked.connect(self.close)
    
    def onReset(self):
        secretKey = self.lineEdit.text()

        if not re.search(self.secretKeyRegex, secretKey):
            self.__notifyUser(QMessageBox.Warning, "Secret Key must contains from 5 to 15 characters, begin with a non-digit character")
            return
        
        self.pushButton.setText("Reseting ...")
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.signals.resetSystem.emit(secretKey)
    
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str, buttons: QMessageBox.StandardButton=QMessageBox.Ok):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        msgBox.setStandardButtons(buttons)
        return msgBox.exec_()