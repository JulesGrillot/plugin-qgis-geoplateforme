# standard
import os

# PyQGIS
from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsProcessingContext,
    QgsProcessingFeedback,
)
from qgis.gui import QgsFileWidget
from qgis.PyQt import QtCore, QtGui, uic
from qgis.PyQt.QtWidgets import QAbstractItemView, QMessageBox, QShortcut, QWidget

# Plugin
from geoplateforme.gui.lne_validators import alphanum_qval
from geoplateforme.gui.upload_creation.mdl_upload_files import UploadFilesTreeModel
from geoplateforme.processing import GeotuileurProvider
from geoplateforme.processing.check_layer import CheckLayerAlgorithm


class UploadCreationWidget(QWidget):
    SUPPORTED_SUFFIX = [
        {"name": "GeoPackage", "suffix": "gpkg"},
        {"name": "Archive", "suffix": "zip"},
        {"name": "CSV", "suffix": "csv"},
    ]

    def __init__(self, parent: QWidget = None):
        """
        Widget to display information for upload creation

        Args:
            parent: (QWidget) parent
        """
        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_upload_creation.ui"), self
        )

        # To avoid some characters
        self.lne_data.setValidator(alphanum_qval)

        self.shortcut_close = QShortcut(QtGui.QKeySequence("Del"), self)
        self.shortcut_close.activated.connect(self.shortcut_del)
        filter_strings = [
            f"{suffix['name']} (*.{suffix['suffix']})"
            for suffix in self.SUPPORTED_SUFFIX
        ]
        self.flw_files_put.setFilter(";;".join(filter_strings))
        self.flw_files_put.fileChanged.connect(self.add_file_path)
        self.flw_files_put.setStorageMode(QgsFileWidget.GetMultipleFiles)

        self.mdl_upload_files = UploadFilesTreeModel(self)
        self.trv_upload_files.setModel(self.mdl_upload_files)
        self.trv_upload_files.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def get_name(self) -> str:
        """
        Get defined name

        Returns: (str) defined name

        """
        return self.lne_data.text()

    def set_name(self, name: str) -> None:
        """
        Define name

        Args:
            name: (str)
        """
        self.lne_data.setText(name)

    def get_crs(self) -> str:
        """
        Get defined crs auth id

        Returns: (str) defined crs auth id

        """
        return self.psw_projection.crs().authid()

    def get_filenames(self) -> [str]:
        """
        Get selected filenames

        Returns: selected filenames

        """
        return self.mdl_upload_files.get_filenames()

    def validateWidget(self) -> bool:
        """
        Validate current content by checking files

        Returns: True if content is valid, False otherwise

        """
        valid = self._check_input_layers()

        if valid and len(self.lne_data.text()) == 0:
            valid = False
            QMessageBox.warning(
                self, self.tr("No name defined."), self.tr("Please define data name")
            )

        if valid and not self.psw_projection.crs().isValid():
            valid = False
            QMessageBox.warning(
                self, self.tr("No SRS defined."), self.tr("Please define SRS")
            )

        return valid

    def _check_input_layers(self) -> bool:
        valid = True

        algo_str = f"{GeotuileurProvider().id()}:{CheckLayerAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        params = {CheckLayerAlgorithm.INPUT_LAYERS: self.get_filenames()}
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        result, success = alg.run(params, context, feedback)

        result_code = result[CheckLayerAlgorithm.RESULT_CODE]

        if result_code != CheckLayerAlgorithm.ResultCode.VALID:
            valid = False
            error_string = self.tr("Invalid layers:\n")
            if CheckLayerAlgorithm.ResultCode.CRS_MISMATCH in result_code:
                error_string += self.tr("- CRS mismatch\n")
            if CheckLayerAlgorithm.ResultCode.INVALID_LAYER_NAME in result_code:
                error_string += self.tr("- invalid layer name\n")
            if CheckLayerAlgorithm.ResultCode.INVALID_FILE_NAME in result_code:
                error_string += self.tr("- invalid file name\n")
            if CheckLayerAlgorithm.ResultCode.INVALID_FIELD_NAME in result_code:
                error_string += self.tr("- invalid field name\n")
            if CheckLayerAlgorithm.ResultCode.INVALID_LAYER_TYPE in result_code:
                error_string += self.tr("- invalid layer type\n")

            error_string += self.tr("Invalid layers list are available in details.")

            msgBox = QMessageBox(
                QMessageBox.Warning, self.tr("Invalid layers"), error_string
            )
            msgBox.setDetailedText(feedback.textLog())
            msgBox.exec()

        return valid

    def shortcut_del(self):
        """
        Create  shortcut which delete a filepath

        """
        # Only use row with invalid parent (row for filename)
        rows = [
            x.row()
            for x in self.trv_upload_files.selectedIndexes()
            if not x.parent().isValid()
        ]
        rows.sort(reverse=True)
        for row in rows:
            self.mdl_upload_files.removeRow(row)

    def add_file_path(self):
        """
        Add the file path to the list Widget

        """
        savepath = self.flw_files_put.filePath()
        for path in QgsFileWidget.splitFilePaths(savepath):
            self._add_file_path_to_list(path)

    def _add_file_path_to_list(self, savepath: str) -> None:
        file_info = QtCore.QFileInfo(savepath)
        if file_info.exists() and file_info.suffix() in [
            suffix["suffix"] for suffix in self.SUPPORTED_SUFFIX
        ]:
            self.mdl_upload_files.add_file(savepath)
            self.trv_upload_files.resizeColumnToContents(self.mdl_upload_files.NAME_COL)
            self.trv_upload_files.expandAll()

            # Define name if empty
            if not self.lne_data.text():
                self.lne_data.setText(self.mdl_upload_files.get_first_file_name())

            # Define CRS if not defined
            if (
                not self.psw_projection.crs().isValid()
                and self.mdl_upload_files.get_first_crs()
            ):
                self.psw_projection.setCrs(
                    QgsCoordinateReferenceSystem(self.mdl_upload_files.get_first_crs())
                )
