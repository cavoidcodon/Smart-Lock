from PyQt5.QtCore import QObject, pyqtSignal
import numpy

class Signals(QObject):
# =================================================================
    checkError = pyqtSignal()
    notEmpty = pyqtSignal()
    empty = pyqtSignal()
# =================================================================

# =================================================================
    verifySuccessed = pyqtSignal(object)
    verifyFailed = pyqtSignal(str)
    noFaceDectect = pyqtSignal()
    verifyError = pyqtSignal()
# =================================================================

# =================================================================
    deleteUser = pyqtSignal(str)
    delUserSuccessed = pyqtSignal()
    delUserFailed = pyqtSignal()
    delUserError = pyqtSignal()
# =================================================================

# =================================================================
    checkFace = pyqtSignal(numpy.ndarray)
    checkFaceSuccessed = pyqtSignal()
    checkFaceFailed = pyqtSignal()
    checkFaceError = pyqtSignal()
# =================================================================

# =================================================================
    takeInformationsCompleted = pyqtSignal(object)
    takeFaceCompeleted = pyqtSignal(list)
    addUser = pyqtSignal(object, list)
    addUserSuccessed = pyqtSignal()
    addUserFailed = pyqtSignal()
    addUserError = pyqtSignal()
# =================================================================

# =================================================================
    changeUserInfor = pyqtSignal(tuple)
    getChangeInforCompleted = pyqtSignal(tuple)  
    changeUserInforSuccessed = pyqtSignal()
    changeUserInforFailed = pyqtSignal()
    changeUserInforError = pyqtSignal()
# =================================================================

# =================================================================
    queryLog = pyqtSignal(object)
    queryLogSuccessed = pyqtSignal(list)
    queryLogFailed = pyqtSignal()
    queryLogError = pyqtSignal()
# =================================================================

# =================================================================
    update = pyqtSignal()
    updateSuccessed = pyqtSignal()
    updateFailed = pyqtSignal()
    updateError = pyqtSignal()
# =================================================================

# =================================================================
    checkUpdate = pyqtSignal()
    checkUpdateSuccessed = pyqtSignal(object)
    checkUpdateFailed = pyqtSignal()
    checkUpdateError = pyqtSignal()
# =================================================================

# =================================================================
    resetSystem = pyqtSignal(str)
    resetError = pyqtSignal()
    resetSuccessed = pyqtSignal()
    resetFailed = pyqtSignal()
# =================================================================

    cameraUnavailable = pyqtSignal()
    getFaceCompeleted = pyqtSignal(numpy.ndarray)    
    getIdPassCompleted = pyqtSignal(object)

    getPassCompleted = pyqtSignal(str)
    sessionDone = pyqtSignal()
    penalty = pyqtSignal()
    closeWindow = pyqtSignal()

    

    addAdminSuccessed = pyqtSignal()
    addAdminFailed = pyqtSignal()