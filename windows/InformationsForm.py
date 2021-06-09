from core.Signals import Signals
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox, QWidget
from ui import Ui_InformationsForm
import re

class InformationsForm(QWidget, Ui_InformationsForm):
    def __init__(self, userIdList):
        super(InformationsForm, self).__init__()
        self.setupUi(self)

        self.signals = Signals()
        self.userIdList = userIdList

        self.userIdRegex = "\D[a-zA-Z0-9_]{5,15}"
        self.passwordRegex = "[0-9]{6,6}"
        self.nameRegex = "^[a-zA-Z]+(([,. -][a-zA-Z ])?[a-zA-Z]*)*$"

        self.okButton.clicked.connect(self.onTake)
        self.cancelButton.clicked.connect(self.close)

    def onTake(self):
        userId = self.lineEdit.text()
        name = self.lineEdit_2.text()
        password = self.lineEdit_3.text()
        verifyPass = self.lineEdit_4.text()

        # Check user input
        if not re.search(self.userIdRegex, userId):
            msgBox = QMessageBox()
            msgBox.setText('Your id must contains from 5 to 15 characters, begin with a non-digit character')
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.exec_()
            return
        
        if not re.search(self.nameRegex, name):
            msgBox = QMessageBox()
            msgBox.setText('Name invalid')
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.exec_()
            return
        
        if not re.search(self.passwordRegex, password):
            msgBox = QMessageBox()
            msgBox.setText('Your password must contains 6 digit character')
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.exec_()
            return

        if verifyPass != password:
            msgBox = QMessageBox()
            msgBox.setText('Verify password incorrect')
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.exec_()
            return

        for id in self.userIdList:
            if userId == id:
                msgBox = QMessageBox()
                msgBox.setText('User id already existed')
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.exec_()
                return
        
        informations = {
            "userId": userId,
            "name": name,
            "password": password
        }

        self.signals.takeInformationsCompleted.emit(informations)
        
