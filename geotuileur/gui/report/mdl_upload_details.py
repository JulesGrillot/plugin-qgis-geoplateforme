import json

from qgis.core import QgsApplication
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QModelIndex, QObject
from qgis.PyQt.QtGui import QIcon, QStandardItemModel

from geotuileur.api.custom_exceptions import UnavailableUploadFileTreeException
from geotuileur.api.upload import Upload, UploadRequestManager
from geotuileur.toolbelt import PlgLogger


class UploadDetailsTreeModel(QStandardItemModel):
    NAME_COL = 0
    VALUE_COL = 1

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel for upload details tree display

        Args:
            parent: QObject parent
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Value")])

    def set_upload(self, upload: Upload) -> None:
        """
        Refresh QStandardItemModel data with current upload

        """
        self.removeRows(0, self.rowCount())

        self._insert_details_row(self.tr("Name"), upload.name)
        self._insert_details_row(self.tr("ID"), upload.id)
        self._insert_details_row(self.tr("SRS"), upload.srs)
        self._insert_details_row(self.tr("Size"), str(f"{upload.size / 1e6} Mo"))

        self._insert_details_row(self.tr("Upload content"), "")
        upload_content_index = self.index(self.rowCount() - 1, self.NAME_COL)
        self.insertColumns(0, self.columnCount(), upload_content_index)
        json_file_tree = self._get_upload_file_tree(upload)
        for data in json_file_tree:
            self._insert_file_tree_item(data, upload_content_index)

    def _get_upload_file_tree(self, upload: Upload) -> dict:
        """
        Get upload file tree from upload tags (in case of deleted Upload) or from a request

        Args:
            upload: Upload

        Returns: (dict) upload file tree

        """
        result = dict
        if upload.tags and "file_tree" in upload.tags:
            file_tree = upload.tags["file_tree"]
            result = json.loads(file_tree)
        else:
            try:
                manager = UploadRequestManager()
                result = manager.get_upload_file_tree(upload.datastore_id, upload.id)
            except UnavailableUploadFileTreeException as exc:
                self.log(
                    self.tr("Can't define upload '{0}' file tree : {1}")
                    .format(upload.id)
                    .format(exc),
                    push=True,
                )
        return result

    def _insert_details_row(
        self, name: str, value: str, parent: QModelIndex = QModelIndex()
    ) -> None:
        row = self.rowCount(parent)
        self.insertRow(row, parent)

        self.setData(self.index(row, self.NAME_COL, parent), name)
        self.setData(self.index(row, self.VALUE_COL, parent), value)

    def _insert_file_tree_item(self, data: dict, parent: QModelIndex) -> None:
        self._insert_details_row(data["name"], "", parent)
        last_row = self.rowCount(parent) - 1
        file_tree_index = self.index(last_row, self.NAME_COL, parent)
        if data["type"] == "file":
            self.setData(
                file_tree_index,
                QIcon(QgsApplication.iconPath("mIconFile.svg")),
                QtCore.Qt.DecorationRole,
            )
        elif data["type"] == "directory":
            self.setData(
                file_tree_index,
                QIcon(QgsApplication.iconPath("mIconFolder.svg")),
                QtCore.Qt.DecorationRole,
            )
        self.setData(
            self.index(last_row, self.VALUE_COL, parent),
            str(f"{data['size']  / 1e6} Mo"),
        )

        if "children" in data:
            self.insertColumns(0, self.columnCount(), file_tree_index)
            for child in data["children"]:
                self._insert_file_tree_item(child, file_tree_index)
