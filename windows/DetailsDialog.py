from PyQt5 import QtGui
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QDialog
from ui import Ui_DetailsDialog

class DetailsDialog(QDialog, Ui_DetailsDialog):
    def __init__(self, userId: str, time: str, mode: str, status: str, image: QImage):
        super(DetailsDialog, self).__init__()
        self.setupUi(self)

        self.label.setText(userId)
        self.label_4.setText(time)
        self.label_6.setText(mode)
        self.label_9.setPixmap(QtGui.QPixmap(image))