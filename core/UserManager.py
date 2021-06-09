from core.Signals import Signals
import io
from PyQt5.QtCore import pyqtSignal
import cv2, numpy
from PIL import Image
import requests, base64
from .ThreadWorker import ThreadWorker
import pandas as pd

class UserManager:
    def __init__(self) -> None:
        self.userDataUrl = 'http://localhost:5000/api/admin/userdata'
        self.userInforList = []
        self.dataFrame = None
        self.signals = Signals()

    def loadUserData(self):
        self.requestThread = ThreadWorker(self.getUserList)
        self.requestThread.successed.connect(self.onGetUserListSuccessed)
        self.requestThread.start()

    def getUserList(self):
        response = requests.get(self.userDataUrl)
        response.raise_for_status()

        return response, response.status_code

    def onGetUserListSuccessed(self, resp, status):
        if status == 200 and ('users' in resp):
            users = resp.get('users')
            dataList = []
            for user in users:
                imageBase64 = user.get('faceBase64')
                imageData = base64.b64decode(str(imageBase64))
                image = Image.open(io.BytesIO(imageData))
                cv2Image = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2RGB)
                infor = UserInfor(id=user.get('userId'), name=user.get('name'), enrollDate=user.get('enrollDate'), role=user.get('role'), faceImage=cv2Image)
                self.userInforList.append(infor)
                tableData = [infor.userId, infor.name, infor.enrollDate, infor.role]
                dataList.append(tableData)

            self.dataFrame = pd.DataFrame(dataList, columns=['User ID', 'Name', 'Enroll Date', 'Role'])
            self.signals.loadDataCompleted.emit()

class UserInfor:
    def __init__(self, id, name, enrollDate, role, faceImage) -> None:
        self.userId = id
        self.name = name
        self.enrollDate = enrollDate
        self.role = role
        self.faceImage = faceImage