from core.Signals import Signals
from .LogInfor import LogInfor
from .ThreadWorker import ThreadWorker
from PIL import Image
import io
import requests
import pandas as pd

class LogManager:
    def __init__(self) -> None:
        self.logUrl = 'http://localhost:5000/api/admin/log'
        self.dataFrame = None
        self.logList = []
        self.signals = Signals()

    def writeLog(self, log: LogInfor):
        self.writeLogRequestThread = ThreadWorker(self.__writeLogRequest, log)
        self.writeLogRequestThread.start()

    def __writeLogRequest(self, log: LogInfor):
        params = {
            'mode': log.mode,
            'user_id': log.userId,
            'is_valid': log.isValid
        }

        if log.image is not None:
            image = Image.fromarray(log.image)
            buff = io.BytesIO()
            image.save(buff, format='JPEG')
            bytesImage = buff.getvalue()
            imageObj = {'image': bytesImage}

            resp = requests.post(self.logUrl, files = imageObj, params=params)
        else:
            resp = requests.post(self.logUrl, params=params)    
        resp.raise_for_status()

        return resp