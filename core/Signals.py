from PyQt5.QtCore import QObject, pyqtSignal
import numpy

class Signals(QObject):
    cameraUnavailable = pyqtSignal()
    getFaceCompeleted = pyqtSignal(numpy.ndarray)
    
    getIdPassCompleted = pyqtSignal(str, str)
    getPassCompleted = pyqtSignal(str)
    sessionDone = pyqtSignal()
    penalty = pyqtSignal()
    closeWindow = pyqtSignal()
    loadDataCompleted = pyqtSignal()

    deleteUser = pyqtSignal(str, int)
    delUserSuccessed = pyqtSignal(int)
    delUserFailed = pyqtSignal()

    changeUserInfor = pyqtSignal(tuple)    
    changeUserInforSuccessed = pyqtSignal(tuple)
    changeUserInforFailed = pyqtSignal()

    checkFace = pyqtSignal(numpy.ndarray)
    checkFaceSuccessed = pyqtSignal()
    checkFaceFailed = pyqtSignal()

    takeInformationsCompleted = pyqtSignal(object)
    takeFaceCompeleted = pyqtSignal(list)
    addUser = pyqtSignal(object, list)
    addUserSuccessed = pyqtSignal(object, str)
    addUserFailed = pyqtSignal()

    queryLog = pyqtSignal(object)
    queryLogSuccessed = pyqtSignal(list)
    queryLogFailed = pyqtSignal()

    checkingNotExisted = pyqtSignal()
    update = pyqtSignal()