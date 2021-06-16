from core.Signals import Signals
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox, QWidget
from ui import Ui_StatusForm
import re

class StatusForm(QWidget, Ui_StatusForm):
    def __init__(self, *args, **kwargs):
        super(StatusForm, self).__init__(*args, **kwargs)
        self.setupUi(self)