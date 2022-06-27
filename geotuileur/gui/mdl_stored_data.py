from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, QSize, Qt, QVariant
from qgis.PyQt.QtGui import QPixmap, QStandardItemModel

from geotuileur.__about__ import DIR_PLUGIN_ROOT
from geotuileur.api.stored_data import StoredData, StoredDataRequestManager
from geotuileur.toolbelt import PlgLogger


class StoredDataListModel(QStandardItemModel):
    NAME_COL = 0
    ID_COL = 1
    TYPE_COL = 2
    STATUT_COL = 3

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel for datastore list display

        Args:
            parent: QObject parent
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels(
            [self.tr("Name"), self.tr("id"), self.tr("Type"), self.tr("Status")]
        )

    def data(self, index: QtCore.QModelIndex, role: int) -> QVariant:
        """
        Override QStandardItemModel data() for :
        - decoration role for status icon

        Args:
            index: QModelIndex
            role: Qt role

        Returns: QVariant

        """
        result = super().data(index, role)
        if role == QtCore.Qt.DecorationRole and index.column() == self.NAME_COL:
            type_ = self.data(
                self.index(index.row(), self.TYPE_COL), QtCore.Qt.DisplayRole
            )
            if type_ == "VECTOR-DB":
                filepath = str(
                    DIR_PLUGIN_ROOT / "resources" / "images" / "dashboard" / "db.png"
                )
            elif type_ == "ROK4-PYRAMID-VECTOR":
                filepath = str(
                    DIR_PLUGIN_ROOT / "resources" / "images" / "dashboard" / "tiles.png"
                )
            result = QPixmap(filepath).scaled(
                QSize(32, 32), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        return result

    def set_datastore(self, datastore: str) -> None:
        """
        Refresh QStandardItemModel data with current datastore stored data

        """
        self.removeRows(0, self.rowCount())

        manager = StoredDataRequestManager()
        try:
            stored_datas = manager.get_stored_data_list(datastore)
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
        self.setData(self.index(row, self.NAME_COL), stored_data.tags, Qt.UserRole)
        self.setData(self.index(row, self.ID_COL), stored_data.id)
        self.setData(self.index(row, self.TYPE_COL), stored_data.type)
        self.setData(self.index(row, self.STATUT_COL), stored_data.status)
