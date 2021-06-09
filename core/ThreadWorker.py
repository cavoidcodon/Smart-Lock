from PyQt5.QtCore import QThread, pyqtSignal
import requests

class ThreadWorker(QThread):
    successed = pyqtSignal(dict, int)
    httpError = pyqtSignal(tuple)
    connectionError = pyqtSignal(str)
    requestError = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs) -> None:
        super(ThreadWorker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        try:
            resp = self.func(*self.args, **self.kwargs)
        except requests.HTTPError as httpError:
            self.httpError.emit((httpError.response.status_code, httpError.response.reason))
        except requests.ConnectionError as connectionError:
            self.connectionError.emit('Connection Error')
        except requests.RequestException as e:
            self.requestError.emit('Request Error')
        else:
            self.successed.emit(resp.json(), resp.status_code)