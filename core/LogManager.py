from core.Signals import Signals
from .LogInfor import LogInfor
from .ThreadWorker import ThreadWorker
from PIL import Image
import io
import requests
import Setings

class LogManager:
    def __init__(self) -> None:
        self.logUrl = "http://{}:{}/api/admin/log".format(Setings.ip_addr, Setings.port)
        self.dataFrame = None
        self.logList = []
        self.signals = Signals()

    def writeLog(self, log: LogInfor):
        self.writeLogRequestThread = ThreadWorker(self.__writeLogRequest, log)
        self.writeLogRequestThread.start()


# Query logs
# =====================================================================
    def query(self, constraints):
        self.queryRequestThread = ThreadWorker(self.__queryLogRequest, constraints)

        self.queryRequestThread.successed.connect(self.onQueryRequestSuccessed)
        self.queryRequestThread.connectionError.connect(lambda message: self.signals.queryLogError.emit())
        self.queryRequestThread.httpError.connect(lambda tupleVal: self.signals.queryLogError.emit())
        self.queryRequestThread.requestError.connect(lambda message: self.signals.queryLogError.emit())
        self.queryRequestThread.start()
    
    def onQueryRequestSuccessed(self, resp, status):
        if status == 200:
            self.signals.queryLogSuccessed.emit(resp['logs'])
        else:
            self.signals.queryLogFailed.emit()

# Private function
# =====================================================================
    def __queryLogRequest(self, infor):

        response = requests.get(self.logUrl, params=infor)
        response.raise_for_status()

        return response

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
# =================================================================================================
# #################################################################################################
# =================================================================================================