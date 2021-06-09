import typing
from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, Qt

class DataModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(DataModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def removeRows(self, row: int, count: int, parent: QModelIndex) -> bool:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)

        for offset in range(0, count):
            self._data.drop(row + offset)
        self.endRemoveRows()
        return True

    def insertRows(self, row: int, count: int, parent: QModelIndex) -> bool:
        self.beginInsertRows(QModelIndex(), row, row+count-1)

        self.endInsertRows()
        return True

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    def setData(self, index: QModelIndex, value: typing.Any, role=Qt.DisplayRole) -> bool:
        if index.isValid():
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False