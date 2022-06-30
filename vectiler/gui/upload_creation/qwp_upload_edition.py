# standard
import os

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.gui import QgsFileWidget
from qgis.PyQt import QtCore, QtGui, uic
from qgis.PyQt.QtWidgets import QAbstractItemView, QMessageBox, QShortcut, QWizardPage

# Plugin
from vectiler.processing import VectilerProvider
from vectiler.processing.check_layer import CheckLayerAlgorithm


class UploadEditionPageWizard(QWizardPage):
    def __init__(self, parent=None):

        """
        QWizardPage to define current geotuileur import data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_upload_edition.ui"), self
        )

        # # To avoid some characters

        rx = QtCore.QRegExp("[a-z-A-Z-0-9-_]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lne_data.setValidator(validator)

        self.lvw_import_data.setSelectionMode(QAbstractItemView.MultiSelection)

        self.shortcut_close = QShortcut(QtGui.QKeySequence("Del"), self)
        self.shortcut_close.activated.connect(self.shortcut_del)

        self.flw_files_put.fileChanged.connect(self.add_file_path)
        self.flw_files_put.setStorageMode(QgsFileWidget.GetMultipleFiles)

        self.setCommitPage(True)

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

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

        algo_str = f"{VectilerProvider().id()}:{CheckLayerAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        params = {CheckLayerAlgorithm.INPUT_LAYERS: self.get_filenames()}
        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        result, success = alg.run(params, context, feedback)

        result_code = result[CheckLayerAlgorithm.RESULT_CODE]

        if result_code != CheckLayerAlgorithm.ResultCode.VALID:
            valid = False
            error_string = self.tr("Invalid layers :\n")
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
        for x in self.lvw_import_data.selectedIndexes():
            row = x.row()
            item = self.lvw_import_data.takeItem(row)
            del item

    def add_file_path(self):

        """
        Add the file path to the list Widget

        """
        savepath = self.flw_files_put.filePath()
        for path in QgsFileWidget.splitFilePaths(savepath):
            self._add_file_path_to_list(path)

    def _add_file_path_to_list(self, savepath):
        if QtCore.QFileInfo(savepath).exists():
            items = self.lvw_import_data.findItems(
                savepath, QtCore.Qt.MatchCaseSensitive
            )
            if len(items) == 0:
                self.lvw_import_data.addItem(savepath)

    def get_filenames(self) -> [str]:
        return [
            self.lvw_import_data.item(row).text()
            for row in range(0, self.lvw_import_data.count())
        ]
