from datetime import datetime

from PyQt5 import QtWidgets
from windows.StatusDialog import StatusDialog
from windows.DetailsDialog import DetailsDialog
from windows.InformationsForm import InformationsForm
from windows.FaceForm import FaceForm
from windows.ChangeInforForm import ChangeInforForm
from core.Signals import Signals
from core.DataModel import DataModel
from ui import Ui_AdminWindow

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QModelIndex, Qt
import pandas, base64, numpy, cv2, io

from PIL import Image

class AdminWindow(QMainWindow, Ui_AdminWindow):
    def __init__(self, users, logs, updateLogs):
        super(AdminWindow, self).__init__()
        self.setupUi(self)

        self.signals = Signals()
        self.users = users
        self.logs = logs
        self.updateLogs = updateLogs

        self.logInforTableView.setModel(DataModel(self.__constructLogsDataFrame(self.logs)))

        self.userDataModel = DataModel(self.__constructUserDataFrame(self.users))
        self.userListTableView.setModel(self.userDataModel)
        self.userSelectionModel = self.userListTableView.selectionModel()
        self.userSelectionModel.selectionChanged.connect(self.onUserListSelectionChanged)
        self.userListTableView.selectRow(0)

        self.logSelectionModel = self.logInforTableView.selectionModel()
        self.logSelectionModel.selectionChanged.connect(self.onLogsSelectionChanged)

        self.updateHistoryTableView.setModel(DataModel(self.__constructUpdateLogsDataFrame(self.updateLogs)))

        # Admin window signal
        self.delUserButton.clicked.connect(self.onDeleteUser)
        self.changeInforButton.clicked.connect(self.onChangeUserInfor)
        self.addUserButton.clicked.connect(self.onAddUser)
        self.pushButton.clicked.connect(self.onShowLog)
        self.queryButton.clicked.connect(self.onQuery)
        self.updateButton.clicked.connect(self.onUpdate)
        self.checkUpdateButton.clicked.connect(self.onCheckUpdate)

# Close event
# =============================================================================================
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        super().closeEvent(a0)
        self.signals.closeWindow.emit()

# =============================================================================================
# Handle item selection
# =============================================================================================
    # User list selection changed
    # ===============================================================
    def onUserListSelectionChanged(self, selected, deselected):
        self.selectedIndexs = selected.indexes()

        if len(self.selectedIndexs) > 0:
            face = QtGui.QPixmap("/home/x6hdm/Code/client/resources/images/avata.jpg") #default face image
            for user in self.users:
                if user.get('userId') == self.userDataModel.data(self.selectedIndexs[0], Qt.DisplayRole):
                    imageBase64 = user.get('faceBase64')
                    qImage = self.__b64Str2QImage(imageBase64)
                    face = QtGui.QPixmap(qImage)

            # Set display informations
            self.label_2.setPixmap(face)
            self.userIDLabel.setText(str(self.userDataModel.data(self.selectedIndexs[0], Qt.DisplayRole)))
            self.nameLabel.setText(str(self.userDataModel.data(self.selectedIndexs[1], Qt.DisplayRole)))
            self.erollDateLabel.setText(str(self.userDataModel.data(self.selectedIndexs[2], Qt.DisplayRole)))
            self.roleLabel.setText(str(self.userDataModel.data(self.selectedIndexs[3], Qt.DisplayRole)))

    def onLogsSelectionChanged(self, selected, deselected):
        self.logSelectedIndexes = selected.indexes()
# ==============================================================================================
# ==============================================================================================





# =============================================================================================
# Handle delete user
# =============================================================================================

    # Slot for deleteUserButton clicked signal
    # =========================================================================================
    def onDeleteUser(self):        
        if len(self.selectedIndexs) == 0:
            self.__notifyUser(QMessageBox.Warning, "Please select user for delete first.")
            return
        
        if self.userDataModel.data(self.selectedIndexs[3], Qt.DisplayRole) == 'Admin':
            self.__notifyUser(QMessageBox.Warning, "Can not delete admin user.")
            return
        
        userId = self.userDataModel.data(self.selectedIndexs[0], Qt.DisplayRole)
        ret = self.__notifyUser(QMessageBox.Warning, f"Do you want to delete {userId}", QMessageBox.Ok | QMessageBox.Cancel)
        if ret == QMessageBox.Ok:
            self.setEnabled(False)
            self.delUserButton.setText('Deleting...')
            self.signals.deleteUser.emit(userId)
        else: 
            return

    # Slot for delUserSuccessed signal
    # =========================================================================================
    def onDelUserSuccessed(self):
        self.delUserButton.setText('Delete')
        delId = self.userDataModel.data(self.selectedIndexs[0], Qt.DisplayRole)

        for user in self.users:
            if user.get('userId') == delId:
                self.users.remove(user)
        
        self.userDataModel.removeRows(self.selectedIndexs[0].row(), 1, QModelIndex())
        self.userListTableView.selectRow(0)
        self.setEnabled(True)
        self.__notifyUser(QMessageBox.Information, "Delete user successful.")

    # Slot for delUserFailed signal
    # =========================================================================================   
    def onDelUserFailed(self):
        self.delUserButton.setText('Delete')
        self.setEnabled(True)
        self.__notifyUser(QMessageBox.Critical, "Delete user failed.")
    
    def onDelUserError(self):
        self.delUserButton.setText('Delete')
        self.setEnabled(True)
        self.__notifyUser(QMessageBox.Critical, "An error occurred.")

# ==============================================================================================
# ==============================================================================================





# =============================================================================================
# Handle change user infor
# =============================================================================================

    # Slot for changeUserInforButton clicked signal
    # =========================================================================================
    def onChangeUserInfor(self):
        self.setEnabled(False)
        role = self.userDataModel.data(self.selectedIndexs[3], Qt.DisplayRole)
        userId = self.userDataModel.data(self.selectedIndexs[0], Qt.DisplayRole)

        self.changeInforForm = ChangeInforForm(userId, role)
        self.changeInforForm.show()
        self.changeInforForm.signals.closeWindow.connect(lambda: self.setEnabled(True))
        self.changeInforForm.signals.getChangeInforCompleted.connect(self.onGetChangeInforCompleted)
    
    def onGetChangeInforCompleted(self, infor):
        self.changeInfor = infor
        self.signals.changeUserInfor.emit(infor)

    def onChangeUserInforSuccessed(self):
        self.changeInforForm.close()
        role = self.changeInfor[2]
        if role == 'Admin' and self.userDataModel.data(self.selectedIndexs[3], Qt.DisplayRole) == 'Normal':
            self.__notifyUser(QMessageBox.Information, "Admin is changed, system will logout!")
            self.close()
        else:
            self.__notifyUser(QMessageBox.Information, "Change user's infor successful")
    
    def onChangeUserInforFailed(self):
        self.changeInforForm.close()
        self.__notifyUser(QMessageBox.Information, "Change user's infor failed")
# ==============================================================================================
# ==============================================================================================





# =============================================================================================
# Handle add user
# =============================================================================================


    # Slot for addUserButton clicked signal
    # =========================================================================================
    def onAddUser(self):
        self.setEnabled(False)
        self.faceForm = FaceForm('checking')
        self.faceForm.start()
        self.faceForm.signals.checkFace.connect(lambda pic: self.signals.checkFace.emit(pic))

    def onCheckFaceSuccessed(self):
        self.faceForm.close()
        self.__notifyUser(QMessageBox.Critical, "Can not add user.")
        self.setEnabled(True)       
    
    def onCheckFaceFailed(self):
        self.faceForm.close()

        userIdList = []
        for user in self.users:
            userIdList.append(user.get('userId'))
        
        self.informationsForm = InformationsForm(userIdList)
        self.informationsForm.signals.takeInformationsCompleted.connect(self.onTakeInformationsCompleted)
        self.informationsForm.show()
    
    def onCheckFaceError(self):
        self.faceForm.close()
        self.__notifyUser(QMessageBox.Critical, "An error occurred.")
        self.setEnabled(True) 

    def onTakeInformationsCompleted(self, infor: object):
        self.informationsForm.close()
        self.addingUserInfor = infor
        self.takingFaceForm = FaceForm('taking')
        self.takingFaceForm.signals.takeFaceCompeleted.connect(self.onTakeFaceCompleted)
        self.takingFaceForm.start()

    def onTakeFaceCompleted(self, faceList):
        self.addingFace = faceList[0]
        self.takingFaceForm.setEnabled(False)
        self.signals.addUser.emit(self.addingUserInfor, faceList)
    
    def onAddUserSuccessed(self):
        self.takingFaceForm.close()
        self.setEnabled(True)
        self.userListTableView.selectRow(0)
        newUser = {
            'userId': self.addingUserInfor['userId'],
            'name': self.addingUserInfor['name'],
            'enrollDate': datetime.today(),
            'role': 'Normal',
            'faceBase64': self.addingFace
        }

        self.users.append(newUser)
        self.userDataModel = DataModel(self.__constructUserDataFrame(self.users))
        self.userListTableView.setModel(self.userDataModel)
        self.userSelectionModel = self.userListTableView.selectionModel()
        self.userSelectionModel.selectionChanged.connect(self.onUserListSelectionChanged)
        self.userListTableView.selectRow(0)

        self.__notifyUser(QMessageBox.Information, "Add user successed.")


    def onAddUserFailed(self):
        self.takingFaceForm.close()
        self.setEnabled(True)
        self.__notifyUser(QMessageBox.Information, "Add user failed.")


# ==============================================================================================
# ==============================================================================================


    


# =============================================================================================
# Handle show log
# =============================================================================================
    def onShowLog(self):
        if len(self.logSelectedIndexes) == 0:
            return
            
        userId = self.logInforTableView.model().data(self.logSelectedIndexes[1], Qt.DisplayRole)
        time = self.logInforTableView.model().data(self.logSelectedIndexes[2], Qt.DisplayRole)
        mode = self.logInforTableView.model().data(self.logSelectedIndexes[0], Qt.DisplayRole)
        status = self.logInforTableView.model().data(self.logSelectedIndexes[3], Qt.DisplayRole)

        for log in self.logs:
            if log['userId'] == userId and log['time'] == time:
                if log['imageBase64'] == 'No Image':
                    showImage = QtGui.QImage("/home/x6hdm/Code/client/resources/images/default-avatar.png")
                else:
                    showImage = self.__b64Str2QImage(log['imageBase64'])
        time = str(time)[:str(time).rfind(":")].replace("T", " ")
        self.detailsDialog = DetailsDialog(userId, time, mode, status, showImage)
        self.detailsDialog.show()
        
    def onQuery(self):
        format = "yyyy-MM-ddTHH:mm"
        userId = self.userIDLineEdit.text()
        mode = self.comboBox.currentText()
        startTime = self.startDateTimeEdit.dateTime().toString(format)
        endTime = self.endDateTimeEdit.dateTime().toString(format)

        self.signals.queryLog.emit({
            'user_id': userId,
            'type': mode,
            'start_time': startTime,
            'end_time': endTime
        })

    def onQueryLogSuccessed(self, logs):
        self.logs = logs
        self.logInforTableView.setModel(DataModel(self.__constructLogsDataFrame(self.logs)))
        self.logSelectionModel = self.logInforTableView.selectionModel()
        self.logSelectionModel.selectionChanged.connect(self.onLogsSelectionChanged)
    
    def onQueryLogFailed(self):
        self.__notifyUser(QMessageBox.Critical, "An error occured.")
# ==============================================================================================
# ==============================================================================================


# =============================================================================================
# Handle update
# =============================================================================================
    def onUpdate(self):
        retVal = self.__notifyUser(QMessageBox.Warning, "Updates may cause the system to slowdown "\
            "during the update time. Do you want to continue?", QMessageBox.Cancel | QMessageBox.Ok)
        
        if retVal == QMessageBox.Ok:
            self.updateButton.setText("Updating...")
            self.updateButton.setEnabled(False)
            self.signals.update.emit()
    
    def onUpdateSuccessed(self):
        self.updateButton.setText("Update")
        self.updateButton.setEnabled(True)
        self.__notifyUser(QMessageBox.Information, "Update Successfull.")
    
    def onUpdateFailed(self):
        self.updateButton.setText("Update")
        self.updateButton.setEnabled(True)
        self.__notifyUser(QMessageBox.Critical, "Update Failed.")
    
    def onUpdateError(self):
        self.updateButton.setText("Update")
        self.updateButton.setEnabled(True)
        self.__notifyUser(QMessageBox.Critical, "An error occurred.")
    
    def onCheckUpdate(self):
        self.checkUpdateButton.setText("Checking ...")
        self.signals.checkUpdate.emit()

    def onCheckUpdateSuccessed(self, resp):
        self.checkUpdateButton.setText("Check Update")
        self.statusDialog = StatusDialog(resp['isNeedUpdate'], resp['status'])
        self.statusDialog.show()
    
    def onCheckUpdateError(self):
        self.checkUpdateButton.setText("Check Update")
        self.__notifyUser(QMessageBox.Critical, "An error occurred.")
# ============================================================================================
# ============================================================================================


# Private function
# ==============================================================================================
    # ===============================================================
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str, buttons: QMessageBox.StandardButton=QMessageBox.Ok):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        msgBox.setStandardButtons(buttons)
        return msgBox.exec_()

    def __constructLogsDataFrame(self, logs):
        dataList = []
        for log in logs:
            rowData = [log['mode'], log['userId'], log['time'], log['status']]
            dataList.append(rowData)
        return pandas.DataFrame(dataList, columns=['Mode', 'User ID', 'Time', 'Status'])
    
    def __constructUpdateLogsDataFrame(self, logs):
        dataList = []
        for log in logs:
            rowData = [log['timeStart'], log['timeEnd'], log['status']]
            dataList.append(rowData)
        return pandas.DataFrame(dataList, columns=['Start', 'End', 'Status'])
    
    def __constructUserDataFrame(self, users):
        dataList = []
        for user in users:
            rowData = [user.get('userId'), user.get('name'), user.get('enrollDate'), user.get('role')]
            dataList.append(rowData)
        return pandas.DataFrame(dataList, columns=['User ID', 'Name', 'Enroll Date', 'Role'])

    def __b64Str2QImage(self, b64Str):
        imageData = base64.b64decode(str(b64Str))
        image = Image.open(io.BytesIO(imageData))
        cv2Image = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2RGB)
        height, width, channel = cv2Image.shape
        bytesPerLine = 3 * width
        return QtGui.QImage(cv2Image.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)
# ===============================================================
    