from core.UserManager import UserManager
from core.LogManager import LogManager
from core.LogInfor import LogInfor
from .Signals import Signals

class Session:
    def __init__(self) -> None:
        self.invalidCount = 0
        self.MAX_ALLOWED_TIMES = 3
        self.signals = Signals()
        self.logManager = LogManager()
        self.userManager = UserManager()

    def start(self):
        pass

    def restart(self):
        pass

    def stop(self):
        pass
