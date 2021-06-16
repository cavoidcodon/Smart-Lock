import json, io, numpy, pandas, requests, base64
from requests.models import Response
from core.Signals import Signals
from PIL import Image
from .ThreadWorker import ThreadWorker
import Setings

class UserManager:
    def __init__(self) -> None:
        self.userDataUrl = "http://{}:{}/api/admin/userdata".format(Setings.ip_addr, Setings.port)
        self.adminUrl = "http://{}:{}/api/admin".format(Setings.ip_addr, Setings.port)
        self.checkingUrl = "http://{}:{}/api/checking".format(Setings.ip_addr, Setings.port)
        self.faceRegUrl = "http://{}:{}/api/face-recognition".format(Setings.ip_addr, Setings.port)
        self.idPassUrl = "http://{}:{}/api/idpassword".format(Setings.ip_addr, Setings.port)
        self.loginAdminUrl = "http://{}:{}/api/admin/login".format(Setings.ip_addr, Setings.port)

        self.userInforList = []
        self.dataFrame = None
        self.signals = Signals()



# ===========================================================================
# Checking system status: has users or empty ?
# ===========================================================================


    def checkSystem(self):
        self.checkingThread = ThreadWorker(self.__checkSystemRequest)
        self.checkingThread.successed.connect(self.onCheckRequestSuccessed)
        self.checkingThread.httpError.connect(lambda x: self.signals.checkError.emit())
        self.checkingThread.connectionError.connect(lambda x: self.signals.checkError.emit())
        self.checkingThread.requestError.connect(lambda x: self.signals.checkError.emit())
        self.checkingThread.start()

    def onCheckRequestSuccessed(self, resp, status):
        if status == 200 and resp['isEmpty']:
            self.signals.empty.emit()
        elif not resp['isEmpty']:
            self.signals.notEmpty.emit()
        else:
            self.signals.checkError.emit()

    def __checkSystemRequest(self):
        response = requests.get(self.checkingUrl)
        response.raise_for_status()

        return response

# ===========================================================================
# ===========================================================================


# ===========================================================================
# Add admin
# ===========================================================================

    def addAdmin(self, infor, faces):
        self.addAdminRequestThread = ThreadWorker(self.__addAdminRequest, infor, faces)
        self.addAdminRequestThread.successed.connect(self.onAddAdminRequestSuccessed)
        self.addAdminRequestThread.connectionError.connect(lambda val: self.signals.addAdminFailed.emit())
        self.addAdminRequestThread.httpError.connect(lambda message: self.signals.addAdminFailed.emit())
        self.addAdminRequestThread.requestError.connect(lambda message: self.signals.addAdminFailed.emit())
        self.addAdminRequestThread.start()
    
    def onAddAdminRequestSuccessed(self, resp, status):
        if status == 200 and resp['result']:
            self.signals.addAdminSuccessed.emit()
        else:
            self.signals.addAdminFailed.emit()

    def __addAdminRequest(self, infor, faces):
        postDict = {
            "user_id": infor['user_id'],
            "name": infor['name'],
            "password": infor['password'],
            "secret_key": infor['secret_key'],
            "faces": faces
        }

        headers = {
            'Content-Type': 'application/json',  # This is important
        }

        response = requests.post(self.adminUrl, data=json.dumps(postDict), headers=headers)
        response.raise_for_status()

        return response

# ===========================================================================
# ===========================================================================



# ===========================================================================
# Verify user
# ===========================================================================

    def verify(self, mode: str, infor: object=None, faceImage: numpy.ndarray=None, password: str=None):
        if mode == 'face-regconition':
            self.verifyThread = ThreadWorker(self.__checkFaceRequest, faceImage)
        elif mode == 'idpass':
            self.verifyThread = ThreadWorker(self.__checkInforRequest, infor)
        else:
            self.verifyThread = ThreadWorker(self.__loginRequest, faceImage, password)
        
        self.verifyThread.successed.connect(self.onVerifyRequestSuccessed)
        self.verifyThread.httpError.connect(lambda x: self.signals.verifyError.emit())
        self.verifyThread.connectionError.connect(lambda x: self.signals.verifyError.emit())
        self.verifyThread.requestError.connect(lambda x: self.signals.verifyError.emit())
        self.verifyThread.start()

    
    def onVerifyRequestSuccessed(self, result, status):
        if status == 200:
            if result['result']:
                self.signals.verifySuccessed.emit(result)
            elif result['status'] == 'No Face':
                self.signals.noFaceDectect.emit()
            else:
                self.signals.verifyFailed.emit(result['status'])
    
    def __checkInforRequest(self, infor):
        respone = requests.post(self.idPassUrl, params=infor)
        respone.raise_for_status()

        return respone

    def __checkFaceRequest(self, faceImage: numpy.ndarray) -> Response:
        image = Image.fromarray(faceImage)
        buff = io.BytesIO()
        image.save(buff, format='JPEG')
        bytesImage = buff.getvalue()
        
        obj = {'image': bytesImage}
        resp = requests.post(self.faceRegUrl, files = obj)
        resp.raise_for_status()

        return resp
    
    def __loginRequest(self, fimage: numpy.ndarray, pwd: str):
        image = Image.fromarray(fimage)
        buff = io.BytesIO()
        image.save(buff, format='JPEG')
        bytesImage = buff.getvalue()
        
        obj = {'image': bytesImage}
        password = {'password': pwd}

        response = requests.post(self.loginAdminUrl, files=obj, params=password)
        response.raise_for_status()

        return response

# ===========================================================================
# ===========================================================================



# ===========================================================================
# Delete User
# ===========================================================================
    def delete(self, userId):
        self.deleteThread = ThreadWorker(self.__deleteUserRequest, userId)
        self.deleteThread.successed.connect(self.onDeleteRequestSuccessed)
        self.deleteThread.connectionError.connect(lambda message: self.signals.delUserError.emit())
        self.deleteThread.httpError.connect(lambda tupleVal: self.signals.delUserError.emit())
        self.deleteThread.requestError.connect(lambda message: self.signals.delUserError.emit())
        self.deleteThread.start()

    def onDeleteRequestSuccessed(self, resp, status):
        if status == 200 and resp['result']:
            self.signals.delUserSuccessed.emit()
        else:
            self.signals.delUserFailed.emit()

    def __deleteUserRequest(self, userId):
        obj = {'user_id': userId}
        resp = requests.delete(self.userDataUrl, params=obj)
        resp.raise_for_status()

        return resp
# ===========================================================================
# ===========================================================================



# ===========================================================================
# Add User
# ===========================================================================
    def add(self, infor, faces):
        self.addUserThread = ThreadWorker(self.__addUserRequest, infor, faces)
        self.addUserThread.successed.connect(self.onAddUserRequestSuccessed)
        self.addUserThread.connectionError.connect(lambda message: self.signals.addUserError.emit())
        self.addUserThread.httpError.connect(lambda tupleVal: self.signals.addUserError.emit())
        self.addUserThread.requestError.connect(lambda message: self.signals.addUserError.emit())
        self.addUserThread.start()

    def onAddUserRequestSuccessed(self, resp, status):
        if status == 200 and resp['result']:
            self.signals.addUserSuccessed.emit()
        else:
            self.signals.addAdminFailed.emit()

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
# ===========================================================================
# ===========================================================================



# ===========================================================================
# Change User Informations
# ===========================================================================
    def changeInfor(self, infor):
        self.changeInforThread = ThreadWorker(self.__changeUserInforRequest, infor)
        self.changeInforThread.successed.connect(self.onChangeInforRequestSuccessed)
        self.changeInforThread.httpError.connect(lambda tupval: self.signals.changeUserInforError.emit())
        self.changeInforThread.connectionError.connect(lambda message: self.signals.changeUserInforError.emit())
        self.changeInforThread.requestError.connect(lambda message: self.signals.changeUserInforError.emit())
        self.changeInforThread.start()

    def onChangeInforRequestSuccessed(self, resp, status):
        if status == 200 and resp['result']:
            self.signals.changeUserInforSuccessed.emit()
        else:
            self.signals.changeUserInforFailed.emit()

    def __changeUserInforRequest(self, infor):
        param = {
            'user_id': infor[0],
            'password': infor[1],
            'role': infor[2]
        }

        resp = requests.put(self.userDataUrl, params=param)
        resp.raise_for_status()

        return resp
# ===========================================================================
# ===========================================================================


class UserInfor:
    def __init__(self, id, name, enrollDate, role, faceImage) -> None:
        self.userId = id
        self.name = name
        self.enrollDate = enrollDate
        self.role = role
        self.faceImage = faceImage