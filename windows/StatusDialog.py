from PyQt5.QtWidgets import QDialog
from ui import Ui_StatusDialog

class StatusDialog(QDialog, Ui_StatusDialog):
    def __init__(self, isNeedToUpdate, status):
        super(StatusDialog, self).__init__()
        self.setupUi(self)

        self.label_2.setText(str(isNeedToUpdate))
        self.textBrowser.setText(status)