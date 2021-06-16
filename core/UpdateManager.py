import Setings
from .Signals import Signals
import requests
from .ThreadWorker import ThreadWorker

class UpdateManager:
    def __init__(self) -> None:
        self.updateUrl = f"http://{Setings.ip_addr}:{Setings.port}/api/update"
        self.resetUrl = f"http://{Setings.ip_addr}:{Setings.port}/api/reset"
        self.signals = Signals()

    def reset(self, key: str):
        self.resetThread = ThreadWorker(self.__resetRequest, key)
        self.resetThread.successed.connect(self.onResetRequestSuccessed)
        self.resetThread.httpError.connect(lambda x: self.signals.resetError.emit())
        self.resetThread.connectionError.connect(lambda x: self.signals.resetError.emit())
        self.resetThread.requestError.connect(lambda x: self.signals.resetError.emit())
        self.resetThread.start()
    
    def onResetRequestSuccessed(self, resp, status):
        if status == 200 and resp["result"]:
            self.signals.resetSuccessed.emit()
        else:
            self.signals.resetError.emit()

    def __resetRequest(self, key:str):
        param = {"secret_key": key}

        resp = requests.post(self.resetUrl, params=param)
        resp.raise_for_status()

        return resp
    
    def checkUpdate(self):
        self.checkUpdateThread = ThreadWorker(self.__checkUpdateRequest)
        self.checkUpdateThread.successed.connect(self.onCheckUpdateRequestSuccessed)
        self.checkUpdateThread.connectionError.connect(lambda message: self.signals.checkUpdateError.emit())
        self.checkUpdateThread.httpError.connect(lambda tupleVal: self.signals.checkUpdateError.emit())
        self.checkUpdateThread.requestError.connect(lambda message: self.signals.checkUpdateError.emit())
        self.checkUpdateThread.start()

    def onCheckUpdateRequestSuccessed(self, resp, status):
        if status == 200 and resp["result"]:
            self.signals.checkUpdateSuccessed.emit(resp)
        else:
            self.signals.checkUpdateError.emit()

    def update(self):
        self.updateThread = ThreadWorker(self.__updateRequest)
        self.updateThread.successed.connect(self.onUpdateRequestSuccessed)
        self.updateThread.connectionError.connect(lambda message: self.signals.updateError.emit())
        self.updateThread.httpError.connect(lambda tupleVal: self.signals.updateError.emit())
        self.updateThread.requestError.connect(lambda message: self.signals.updateError.emit())
        self.updateThread.start()
    
    def onUpdateRequestSuccessed(self, resp, status):
        if status == 200 and resp['result']:
            self.signals.updateSuccessed.emit()
        else:
            self.signals.updateFailed.emit()
    
    def __checkUpdateRequest(self):
        response = requests.get(self.updateUrl)
        response.raise_for_status()

        return response

    def __updateRequest(self):
        response = requests.post(self.updateUrl)
        response.raise_for_status()

        return response