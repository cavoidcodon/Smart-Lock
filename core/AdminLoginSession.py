from core.LogInfor import LogInfor
import numpy, io, requests, json
from core.Signals import Signals
from PyQt5.QtWidgets import QMessageBox
from PIL import Image
from PIL.Image import fromarray
from .ThreadWorker import ThreadWorker
from .Session import Session
from windows import PasswordForm, FaceRegWindow, AdminWindow


class AdminLoginSession(Session):
    def __init__(self) -> None:
        super().__init__()

        self.signals = Signals()
        self.loginAdminUrl = 'http://localhost:5000/api/admin/login'
        self.userDataUrl = 'http://localhost:5000/api/admin/userdata'
        self.checkFaceUrl = 'http://localhost:5000/api/checking'
        self.logUrl = 'http://localhost:5000/api/admin/log'
        self.updateUrl = 'http://localhost:5000/api/update'

        self.passwordWindow = PasswordForm()
        self.faceRegWindow = FaceRegWindow(timeout=5)

        # Connect window signals to session's slots
        self.faceRegWindow.signals.closeWindow.connect(self.onCloseWindow)
        self.faceRegWindow.signals.getFaceCompeleted.connect(self.onGetFaceCompleted)
        self.faceRegWindow.signals.cameraUnavailable.connect(self.onCameraUnavailable)

        self.passwordWindow.signals.closeWindow.connect(self.onCloseWindow)
        self.passwordWindow.signals.getPassCompleted.connect(self.onGetPassCompleted)



# Implement Session Interface
# ==========================================================================================
    # Start session
    # ==================================================================
    def start(self):
        self.faceRegWindow.start()

    # Restart session
    # ==================================================================
    def restart(self):
        self.passwordWindow.hide()
        self.passwordWindow.clearContent()
        self.faceRegWindow.restart()
# =========================================================================================





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
#   Begin: Handle signals of faceRegWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Handle getFaceCompleted signal from faceRegWindow
    # ======================================================================================
    def onGetFaceCompleted(self, face):
        self.faceImg = face
        self.faceRegWindow.hide()
        self.passwordWindow.show()

    # Handle camera unavailable case
    # ======================================================================================
    def onCameraUnavailable(self):
        self.__notifyUser(QMessageBox.Critical, "Can not open camera.")
        self.faceRegWindow.close()
    
    # Handle close window signal from faceRegWindow
    # Emit sessionDone signal to system
    # ======================================================================================
    def onCloseWindow(self):
        self.signals.sessionDone.emit()


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
#   End: Handle signals of faceRegWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
#   Begin: Handle signals of passwordForm
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Handle getPassCompleted signal from passwordForm
    # ======================================================================================
    def onGetPassCompleted(self, pwd):
        self.checkInforThread = ThreadWorker(self.__loginRequest, self.faceImg, pwd)
        self.checkInforThread.successed.connect(self.onLoginRequestSuccessed)
        self.checkInforThread.httpError.connect(self.onLoginRequestHttpError)
        self.checkInforThread.connectionError.connect(self.onLoginRequestConnectionError)
        self.checkInforThread.requestError.connect(self.onLoginRequestConnectionError)
        self.checkInforThread.start()


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
#   End: Handle signals of passwordForm
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# Begin: Handle signals of loginRequest
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Handle request successed signal from loginRequest
    # ======================================================================================
    def onLoginRequestSuccessed(self, result, status):
        if status == 200 and result.get('existed'):
            self.passwordWindow.hide()
            logInfor = LogInfor(mode='Login', isValid='Valid', userId=result['label'], image=self.faceImg)
            self.logManager.writeLog(logInfor)
            self.__loadUserData()
        else:
            self.invalidCount += 1
            if self.invalidCount >= self.MAX_ALLOWED_TIMES:
                self.__notifyUser(QMessageBox.Critical, "You have logged in more times than allowed!")
                logInfor = LogInfor(mode='Login', isValid='Invalid', userId=result['label'], image=self.faceImg)
                self.logManager.writeLog(logInfor)
                self.passwordWindow.close()
            else:
                ret = self.__notifyUser(QMessageBox.Critical, "Login falied, try again ?", \
                    QMessageBox.Ok | QMessageBox.Cancel)
                if ret == QMessageBox.Ok:
                    self.restart()
                else:
                    self.passwordWindow.close()
                    
    # Handle connection error when login request
    # ======================================================================================
    def onLoginRequestConnectionError(self, str):
        self.__notifyUser(QMessageBox.Critical, f"{str}")
        self.passwordWindow.close()


    # Handle http error when login request
    # ======================================================================================
    def onLoginRequestHttpError(self, tupleVal):
        self.__notifyUser(QMessageBox.Critical, f"An error occurred: {tupleVal[0]}, {tupleVal[1]}")
        self.passwordWindow.close()


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# End: Handle signals of loginRequest
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# Begin: Handle signals of loadUserDataRequest
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Handle request successed signal from loadUserDataRequest
    # ======================================================================================
    def onLoadUserDataSuccessed(self, resp, status):
        if status == 200 and resp['users'] and resp['logs']:
            self.adminWindow = AdminWindow(users=resp['users'], logs=resp['logs'])
            self.adminWindow.signals.closeWindow.connect(self.onCloseWindow)

            # Connect signals from admin window:
            #   + deleteUser signal
            #   + changeUserInfor signal
            self.adminWindow.signals.deleteUser.connect(self.onDeleteUser)
            self.signals.delUserSuccessed.connect(self.adminWindow.onDelUserSuccessed)
            self.signals.delUserFailed.connect(self.adminWindow.onDelUserFailed)

            self.adminWindow.signals.changeUserInfor.connect(self.onChangeUserInfor)
            self.signals.changeUserInforSuccessed.connect(self.adminWindow.onChangeUserInforSuccessed)
            self.signals.changeUserInforFailed.connect(self.adminWindow.onChangeUserInforFailed)

            self.adminWindow.signals.checkFace.connect(self.onCheckFace)
            self.signals.checkFaceSuccessed.connect(self.adminWindow.onCheckFaceSuccessed)
            self.signals.checkFaceFailed.connect(self.adminWindow.onCheckFaceFailed)

            self.adminWindow.signals.addUser.connect(self.onAddUser)
            self.signals.addUserSuccessed.connect(self.adminWindow.onAddUserSuccessed)
            self.signals.addUserFailed.connect(self.adminWindow.onAddUserFailed)

            self.adminWindow.signals.queryLog.connect(self.onQueryLog)
            self.signals.queryLogSuccessed.connect(self.adminWindow.onQueryLogSuccessed)
            self.signals.queryLogFailed.connect(self.adminWindow.onQueryLogFailed)

            self.adminWindow.signals.update.connect(self.onUpdate)        
            
            self.adminWindow.show()

    # Handle request failed signal from loadUserDataRequest
    # ======================================================================================
    def onLoadUserDataFailed(self):
        self.__notifyUser(QMessageBox.Critical, "Can not load user data.")
        self.signals.sessionDone.emit()


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# End: Handle signals of loadUserDataRequest
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# Begin: Handle signal deleteUser of adminWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|

    # Send delete user request
    # ==============================================================================================
    def onDeleteUser(self, userId, row):
        self.queryRequestThread = ThreadWorker(self.__deleteUserRequest, userId)
        # Emit signal to update admin window data
        # Delete the deleted user's row
        self.queryRequestThread.successed.connect(lambda resp, status: self.onDelUserRequestSuccessed(resp, status, row))
        self.queryRequestThread.connectionError.connect(lambda message: self.signals.delUserFailed.emit())
        self.queryRequestThread.httpError.connect(lambda tupleVal: self.signals.delUserFailed.emit())
        self.queryRequestThread.requestError.connect(lambda message: self.signals.delUserFailed.emit())
        self.queryRequestThread.start()

    # Handle del user request successed
    # ==============================================================================================
    def onDelUserRequestSuccessed(self, resp, status, row):
        if status == 200 and resp['result'] == 'User deleted':
            self.signals.delUserSuccessed.emit(row)
        else:
            self.signals.delUserFailed.emit()



# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# End: Handle signal deleteUser of adminWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# Begin: Handle signal changeUserInfor of adminWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|

    # Send change user infor request
    # ==============================================================================================
    def onChangeUserInfor(self, infor):
        self.changeInforThread = ThreadWorker(self.__changeUserInforRequest, infor)
        self.changeInforThread.successed.connect(lambda resp, status: self.onChangeUserInforRequestSuccessed(resp, status, infor))
        self.changeInforThread.httpError.connect(lambda tupval: self.signals.changeUserInforFailed.emit())
        self.changeInforThread.connectionError.connect(lambda message: self.signals.changeUserInforFailed.emit())
        self.changeInforThread.requestError.connect(lambda message: self.signals.changeUserInforFailed.emit())
        self.changeInforThread.start()
    
    # Handle change user infor request successed
    # ==============================================================================================
    def onChangeUserInforRequestSuccessed(self, resp, status, infor):
        if status == 200 and resp['result'] == 'Successed':
            self.signals.changeUserInforSuccessed.emit(infor)
        else:
            self.signals.changeUserInforFailed.emit()


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# End: Handle signal changeUserInfor of adminWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# Begin: Handle signal addUser of adminWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|

    # Handle checkFace signal form adminWindow
    # ===============================================================
    def onCheckFace(self, face):
        self.checkFaceRequestThread = ThreadWorker(self.__checkFaceRequest, face)
        self.checkFaceRequestThread.successed.connect(self.onCheckFaceRequestSuccessed)
        self.checkFaceRequestThread.httpError.connect(lambda tupval: self.signals.checkFaceFailed.emit())
        self.checkFaceRequestThread.connectionError.connect(lambda message: self.signals.checkFaceFailed.emit())
        self.checkFaceRequestThread.requestError.connect(lambda message: self.signals.checkFaceFailed.emit())
        self.checkFaceRequestThread.start()
    
    def onCheckFaceRequestSuccessed(self, resp, status):
        if (status == 200) and (not resp['existed']) and (resp['status'] == 'Not Existed'):
            self.signals.checkFaceSuccessed.emit()
        else:
            self.signals.checkFaceFailed.emit()
    
    def onAddUser(self, infor, listFace):
        self.addUserRequestThread = ThreadWorker(self.__addUserRequest, infor, listFace)
        self.addUserRequestThread.successed.connect(lambda resp, status: \
            self.onAddUserRequestSuccessed(resp, status, infor, listFace[0]))
        self.addUserRequestThread.httpError.connect(lambda tupval: self.signals.addUserFailed.emit())
        self.addUserRequestThread.requestError.connect(lambda message: self.signals.addUserFailed.emit())
        self.addUserRequestThread.connectionError.connect(lambda message: self.signals.addUserFailed.emit())
        self.addUserRequestThread.start()
    
    def onAddUserRequestSuccessed(self, resp, status, infor: object, imageB64Str: str):
        if status == 200 and resp['result'] == 'Successed':
            self.signals.addUserSuccessed.emit(infor, imageB64Str)
        else:
            self.signals.addUserFailed.emit()

# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# End: Handle signal addUser of adminWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|





# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# Begin: Handle signal queryLog of adminWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|


    # Send query log user request
    # ==============================================================================================
    def onQueryLog(self, infor):
        self.queryRequestThread = ThreadWorker(self.__queryLogRequest, infor)
        # Emit signal to update admin window data
        # Delete the deleted user's row
        self.queryRequestThread.successed.connect(self.onQueryLogRequestSuccessed)
        self.queryRequestThread.connectionError.connect(lambda message: self.signals.queryLogFailed.emit())
        self.queryRequestThread.httpError.connect(lambda tupleVal: self.signals.queryLogFailed.emit())
        self.queryRequestThread.requestError.connect(lambda message: self.signals.queryLogFailed.emit())
        self.queryRequestThread.start()

    def onQueryLogRequestSuccessed(self, resp, status):
        if status == 200:
            self.signals.queryLogSuccessed.emit(resp['logs'])
        else:
            self.signals.queryLogFailed.emit()
            


# ==================================================================================================|
# --------------------------------------------------------------------------------------------------|
# End: Handle signal queryLog of adminWindow
# --------------------------------------------------------------------------------------------------|
# ==================================================================================================|



    def onUpdate(self):
        self.updateRequestThread = ThreadWorker(self.__updateRequest)
        # Emit signal to update admin window data
        # Delete the deleted user's row
        self.updateRequestThread.successed.connect(self.onUpdateRequestSuccessed)
        # self.updateRequestThread.connectionError.connect(lambda message: self.signals.queryLogFailed.emit())
        # self.updateRequestThread.httpError.connect(lambda tupleVal: self.signals.queryLogFailed.emit())
        # self.updateRequestThread.requestError.connect(lambda message: self.signals.queryLogFailed.emit())
        self.updateRequestThread.start()

    def onUpdateRequestSuccessed(self, resp, status):
        print(resp, status)

# Private function
# ======================================================================================
    # ==============================================================
    def __updateRequest(self):
        response = requests.post(self.updateUrl)
        response.raise_for_status()

        return response

    # ==============================================================
    def __queryLogRequest(self, infor):

        response = requests.get(self.logUrl, params=infor)
        response.raise_for_status()

        return response

    # ==============================================================
    def __addUserRequest(self, infor, listFace):
        postDict = {
            "user_id": infor['userId'],
            "name": infor['name'],
            "password": infor['password'],
            "faces": listFace
        }

        headers = {
            'Content-Type': 'application/json',  # This is important
        }

        response = requests.post(self.userDataUrl, data=json.dumps(postDict), headers=headers)
        response.raise_for_status()

        return response

    # ==============================================================
    def __checkFaceRequest(self, faceImage):
        image = Image.fromarray(faceImage)
        buff = io.BytesIO()
        image.save(buff, format='JPEG')
        bytesImage = buff.getvalue()
        
        obj = {'image': bytesImage}
        resp = requests.post(self.checkFaceUrl, files = obj)
        resp.raise_for_status()

        return resp

    # ==============================================================
    def __changeUserInforRequest(self, infor):
        param = {
            'user_id': infor[0],
            'password': infor[1],
            'role': infor[2]
        }

        resp = requests.put(self.userDataUrl, params=param)
        resp.raise_for_status()

        return resp

    # ==============================================================
    def __deleteUserRequest(self, userId):
        obj = {
            'user_id': userId
        }
        resp = requests.delete(self.userDataUrl, params=obj)
        resp.raise_for_status()

        return resp

    # ==============================================================
    def __loadUserData(self):
        self.loadUserDataThread = ThreadWorker(self.__loadUserDataRequest)
        self.loadUserDataThread.successed.connect(self.onLoadUserDataSuccessed)
        self.loadUserDataThread.connectionError.connect(self.onLoadUserDataFailed)
        self.loadUserDataThread.httpError.connect(self.onLoadUserDataFailed)
        self.loadUserDataThread.requestError.connect(self.onLoadUserDataFailed)
        self.loadUserDataThread.start()
    
    # ======================================================================================
    def __loadUserDataRequest(self):
        response = requests.get(self.userDataUrl)
        response.raise_for_status()

        return response
    
    # ======================================================================================
    def __loginRequest(self, fimage: numpy.ndarray, pwd: str):
        image = Image.fromarray(fimage)
        buff = io.BytesIO()
        image.save(buff, format='JPEG')
        bytesImage = buff.getvalue()
        
        obj = {'image': bytesImage}
        password = {
            'password': pwd
        }

        response = requests.post(self.loginAdminUrl, files=obj, params=password)
        response.raise_for_status()

        return response
    
    # ======================================================================================
    def __notifyUser(self, iconType: QMessageBox.Icon, message: str, buttons: QMessageBox.StandardButton=QMessageBox.Ok):
        msgBox = QMessageBox()
        msgBox.setIcon(iconType)
        msgBox.setText(message)
        msgBox.setStandardButtons(buttons)
        return msgBox.exec_()

# =================================================================================================
# #################################################################################################
# =================================================================================================
    
    
