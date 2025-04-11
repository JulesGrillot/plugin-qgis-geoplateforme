from osgeo import ogr
from qgis.core import QgsApplication, QgsVectorLayer
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, QVariant
from qgis.PyQt.QtGui import QIcon, QStandardItemModel

from geoplateforme.toolbelt import PlgLogger


class UploadFilesTreeModel(QStandardItemModel):
    NAME_COL = 0
    CSR_COL = 1
    ID_COL = 2

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel for upload file list display

        Args:
            parent: QObject parent
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels(
            [
                self.tr("Name"),
                self.tr("CRS"),
            ]
        )

    def get_filenames(self) -> [str]:
        """
        Get displayed filename list

        Returns: [str] filename list

        """
        result = [
            self.data(self.index(row, self.NAME_COL))
            for row in range(0, self.rowCount())
        ]
        return result

    def get_first_file_name(self) -> str:
        """
        Get first defined filename

        Returns: (str) first file name defined

        """
        row = self.rowCount()
        if row > 0:
            filename = self.data(self.index(0, self.NAME_COL), QtCore.Qt.DisplayRole)
            fileinfo = QtCore.QFileInfo(filename)
            return fileinfo.baseName()
        else:
            return ""

    def get_first_crs(self) -> str:
        """
        Get first defined crs auth id, empty str if no crs defined

        Returns: (str)

        """
        result = ""

        # For all files
        for row in range(0, self.rowCount()):
            parent = self.index(row, self.NAME_COL)

            # Get first defined crs
            for layer_row in range(0, self.rowCount(parent)):
                crs = self.data(self.index(layer_row, self.CSR_COL, parent))
                if crs is not None:
                    result = crs
                    # break for layers in file
                    break
            # Break if a crs was defined in this file
            if result:
                break
        return result

    def data(
        self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole
    ) -> QVariant:
        """
        Override QStandardItemModel data() for :
        - decoration role for CRS icon if invalid value

        Args:
            index: QModelIndex
            role: Qt role

        Returns: QVariant

        """
        result = super().data(index, role)

        if role == QtCore.Qt.DecorationRole:
            if index.column() == self.CSR_COL:
                crs = self.data(index, QtCore.Qt.DisplayRole)
                if crs is not None:
                    first_crs = self.get_first_crs()
                    valid = ("EPSG:" in crs or "IGNF" in crs) and crs == first_crs
                    if valid:
                        result = QIcon(QgsApplication.iconPath("mIconSuccess.svg"))
                    else:
                        result = QIcon(QgsApplication.iconPath("mIconWarning.svg"))
            elif index.column() == self.NAME_COL and not index.parent().isValid():
                filename = self.data(index, QtCore.Qt.DisplayRole)
                fileinfo = QtCore.QFileInfo(filename)
                if not fileinfo.exists():
                    result = QIcon(QgsApplication.iconPath("mIconWarning.svg"))
                elif fileinfo.suffix() == "gpkg":
                    result = QIcon(QgsApplication.iconPath("mGeoPackage.svg"))
                elif fileinfo.suffix() == "zip":
                    result = QIcon(QgsApplication.iconPath("mIconZip.svg"))
                else:
                    result = QIcon(QgsApplication.iconPath("mIconFile.svg"))
        elif role == QtCore.Qt.ToolTipRole:
            if index.column() == self.CSR_COL:
                crs = self.data(index, QtCore.Qt.DisplayRole)
                if crs is not None:
                    first_crs = self.get_first_crs()
                    valid = "EPSG:" in crs or "IGNF" in crs
                    if not valid:
                        result = self.tr(
                            "Invalid CRS. Only EPSG and IGNF crs are supported."
                        )
                    elif crs != first_crs:
                        result = self.tr("Invalid CRS {0}. Expected {1}").format(
                            crs, first_crs
                        )

            elif index.column() == self.NAME_COL and not index.parent().isValid():
                filename = self.data(index, QtCore.Qt.DisplayRole)
                fileinfo = QtCore.QFileInfo(filename)
                if not fileinfo.exists():
                    result = self.tr("File not available.")
        return result

    def add_file(self, filename: str) -> None:
        """
        Add file to model

        Args:
            filename: (str) file name
        """
        row = self._get_file_row(filename)
        if row == -1:
            self._insert_file(filename)

    def _get_file_row(self, filename: str) -> int:
        """
        Get filename row , returns -1 if filename not available

        Args:
            filename: (str) stored data id

        Returns: (int) filename row, -1 if filename not available

        """
        result = -1
        for row in range(0, self.rowCount()):
            if self.data(self.index(row, self.NAME_COL)) == filename:
                result = row
                break
        return result

    def _insert_file(self, filename: str) -> None:
        """
        Insert file and add layers as children. If file doesn't exist it's not added

        Args:
            filename: (str) filename
        """
        row = self.rowCount()
        self.insertRow(row)

        self.setData(self.index(row, self.NAME_COL), filename)
        parent = self.index(row, self.NAME_COL)

        self.insertColumns(0, self.columnCount(), parent)

        # Load layers from gpkg
        fileinfo = QtCore.QFileInfo(filename)
        if fileinfo.exists() and fileinfo.suffix() == "gpkg":
            for l in ogr.Open(filename):
                layer_name = l.GetName()
                layer = QgsVectorLayer(f"{filename}|layername={layer_name}", layer_name)
                if layer.isValid():
                    row = self.rowCount(parent)
                    self.insertRow(row, parent)
                    self.setData(self.index(row, self.NAME_COL, parent), layer_name)
                    self.setData(
                        self.index(row, self.CSR_COL, parent), layer.crs().authid()
                    )
