# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, QSize, Qt, QVariant
from qgis.PyQt.QtGui import QIcon, QPixmap, QStandardItemModel

# plugin
from geotuileur.api.custom_exceptions import ReadUploadException
from geotuileur.api.upload import Upload, UploadRequestManager, UploadStatus
from geotuileur.api.utils import as_datetime
from geotuileur.toolbelt import PlgLogger


class UploadListModel(QStandardItemModel):
    NAME_COL = 0
    DATE_COL = 1
    ID_COL = 2
    STATUS_COL = 3
    DELETE_COL = 4

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel for upload list display

        Args:
            parent: QObject parent
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels(
            [
                self.tr("Name"),
                self.tr("Date"),
                self.tr("id"),
                self.tr("Status"),
                self.tr("Delete"),
            ]
        )

    def get_upload_row(self, upload_id: str) -> int:
        """
        Get upload row from upload id, returns -1 if upload not available

        Args:
            upload_id: (str) upload id

        Returns: (int) upload id row, -1 if upload not available

        """
        result = -1
        for row in range(0, self.rowCount()):
            if self.data(self.index(row, self.ID_COL)) == upload_id:
                result = row
                break
        return result

    def data(
        self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole
    ) -> QVariant:
        """
        Override QStandardItemModel data() for :
        - decoration role for status icon

        Args:
            index: QModelIndex
            role: Qt role

        Returns: QVariant

        """
        result = super().data(index, role)
        if role == QtCore.Qt.DecorationRole:
            if index.column() == self.STATUS_COL:
                status_value = self.data(index, QtCore.Qt.DisplayRole)
                result = self._get_status_icon(UploadStatus[status_value])
            elif index.column() == self.DELETE_COL:
                result = QIcon(QgsApplication.iconPath("mActionRemove.svg"))

        return result

    @staticmethod
    def _get_status_icon(status: UploadStatus) -> QPixmap:
        if status == UploadStatus.CREATED:
            result = QIcon(QgsApplication.iconPath("mTaskQueued.svg")).pixmap(
                QSize(16, 16)
            )
        elif (
            status == UploadStatus.GENERATING
            or status == UploadStatus.CHECKING
            or status == UploadStatus.MODIFYING
        ):
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == UploadStatus.UNSTABLE:
            result = QIcon(QgsApplication.iconPath("mIconWarning.svg")).pixmap(
                QSize(16, 16)
            )
        else:
            result = QIcon(QgsApplication.iconPath("mIconSuccess.svg")).pixmap(
                QSize(16, 16)
            )
        return result

    def set_datastore(self, datastore: str) -> None:
        """
        Refresh QStandardItemModel data with current datastore upload

        """
        self.removeRows(0, self.rowCount())

        manager = UploadRequestManager()
        try:
            uploads = manager.get_upload_list(datastore)
            for upload in uploads:
                self.insert_upload(upload)
        except ReadUploadException as exc:
            self.log(
                f"Error while getting upload informations: {exc}",
                log_level=2,
                push=False,
            )

    def insert_upload(self, upload: Upload) -> None:
        row = self.rowCount()
        self.insertRow(row)

        self.setData(self.index(row, self.NAME_COL), upload.name)
        self.setData(self.index(row, self.NAME_COL), upload, Qt.UserRole)
        self.setData(
            self.index(row, self.DATE_COL),
            as_datetime(upload.get_last_event_date()),
        )
        self.setData(self.index(row, self.ID_COL), upload.id)
        self.setData(self.index(row, self.STATUS_COL), upload.status)
