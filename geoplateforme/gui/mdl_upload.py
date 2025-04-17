from typing import Optional

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, QSize, Qt, QVariant
from qgis.PyQt.QtGui import QIcon, QPixmap, QStandardItemModel

# plugin
from geoplateforme.api.custom_exceptions import ReadUploadException
from geoplateforme.api.upload import Upload, UploadRequestManager, UploadStatus
from geoplateforme.api.utils import as_datetime
from geoplateforme.toolbelt import PlgLogger


class UploadListModel(QStandardItemModel):
    NAME_COL = 0
    DATE_COL = 1
    ID_COL = 2
    STATUS_COL = 3
    DELETE_COL = 4

    def __init__(self, parent: QObject = None):
        """QStandardItemModel for upload list display

        :param parent: parent
        :type parent: QObject
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
        """Get upload row from upload id, returns -1 if upload not available

        :param upload_id: upload id
        :type upload_id: str

        :return: upload id row, -1 if upload not available
        :rtype: int
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
        """Override QStandardItemModel data() for decoration role for status icon

        Args:
        :param index: index
        :type index: QModelIndex
        :param role: Qt role
        :type role: int

        :return: data at index with role
        :rtype: QVariant
        """
        result = super().data(index, role)
        if role == QtCore.Qt.DecorationRole:
            if index.column() == self.STATUS_COL:
                status_value = self.data(index, QtCore.Qt.DisplayRole)
                result = self._get_status_icon(status_value)
            elif index.column() == self.DELETE_COL:
                result = QIcon(QgsApplication.iconPath("mActionRemove.svg"))

        return result

    @staticmethod
    def _get_status_icon(status: UploadStatus) -> QPixmap:
        """Return icon from an upload status

        Args:
        :param status: upload status
        :type status: UploadStatus

        :return: pixmap icon
        :rtype: QPixmap
        """
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

    def set_datastore(
        self, datastore_id: str, dataset_name: Optional[str] = None
    ) -> None:
        """Refresh QStandardItemModel data with current datastore upload

        :param datastore_id: datastore id
        :type datastore_id: str
        :param dataset_name: dataset name
        :type dataset_name: str, optional
        """
        self.removeRows(0, self.rowCount())

        manager = UploadRequestManager()
        try:
            if dataset_name:
                tags = {"datasheet_name": dataset_name}
                uploads = manager.get_upload_list(datastore_id, tags)
            else:
                uploads = manager.get_upload_list(datastore_id)
            for upload in uploads:
                self.insert_upload(upload)
        except ReadUploadException as exc:
            self.log(
                f"Error while getting upload informations: {exc}",
                log_level=2,
                push=False,
            )

    def insert_upload(self, upload: Upload) -> None:
        """Insert upload in model

        :param upload: upload to insert
        :type upload: Upload
        """
        row = self.rowCount()
        self.insertRow(row)

        self.setData(self.index(row, self.NAME_COL), upload.name)
        self.setData(self.index(row, self.NAME_COL), upload, Qt.ItemDataRole.UserRole)
        self.setData(
            self.index(row, self.DATE_COL),
            as_datetime(upload.get_last_event_date()),
        )
        self.setData(self.index(row, self.ID_COL), upload._id)
        self.setData(self.index(row, self.STATUS_COL), upload.status)
