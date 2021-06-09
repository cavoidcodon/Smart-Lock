import numpy


class LogInfor:
    def __init__(self, mode: str, isValid: str, userId: str,  image: numpy.ndarray=None) -> None:
        self.mode = mode
        self.isValid = isValid
        self.image = image
        self.userId = userId