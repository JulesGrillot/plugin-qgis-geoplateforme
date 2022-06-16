from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QStandardItemModel

from vectiler.api.stored_data import StoredDataRequestManager, StoredData
from vectiler.toolbelt import PlgLogger


class StoredDataListModel(QStandardItemModel):
    NAME_COL = 0
    ID_COL = 1
    TYPE_COL = 2

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel for datastore list display

        Args:
            parent: QObject parent
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels([self.tr("Name"), self.tr("id"), self.tr("Type")])

    def set_datastore(self, datastore: str) -> None:
        """
        Refresh QStandardItemModel data with current datastore stored data

        """
        self.removeRows(0, self.rowCount())

        manager = StoredDataRequestManager()
        try:
            stored_datas = manager.get_stored_data(datastore)
            for stored_data in stored_datas:
                self.insert_stored_data(stored_data)
        except StoredDataRequestManager.ReadStoredDataException as exc:
            self.log(
                f"Error while getting stored data informations: {exc}",
                log_level=2,
                push=False,
            )

    def insert_stored_data(self, stored_data: StoredData) -> None:
        row = self.rowCount()
        self.insertRow(row)

        self.setData(self.index(row, self.NAME_COL), stored_data.name)
        self.setData(self.index(row, self.NAME_COL), stored_data.tags, QtCore.Qt.UserRole)
        self.setData(self.index(row, self.ID_COL), stored_data.id)
        self.setData(self.index(row, self.TYPE_COL), stored_data.type)
