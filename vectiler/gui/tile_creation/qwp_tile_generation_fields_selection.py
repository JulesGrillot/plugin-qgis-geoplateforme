# standard
import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox, QWizardPage
from qgis.PyQt import uic

from vectiler.api.stored_data import StoredDataRequestManager
from vectiler.gui.tile_creation.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)


class TileGenerationFieldsSelectionPageWizard(QWizardPage):
    def __init__(
        self, qwp_tile_generation_edition: TileGenerationEditionPageWizard, parent=None
    ):

        """
        QWizardPage to define fields for tile generation

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.qwp_tile_generation_edition = qwp_tile_generation_edition

        uic.loadUi(
            os.path.join(
                os.path.dirname(__file__), "qwp_tile_generation_fields_selection.ui"
            ),
            self,
        )

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.lwg_attribut.clear()
        try:
            manager = StoredDataRequestManager()
            datastore_id = (
                self.qwp_tile_generation_edition.cbx_datastore.current_datastore_id()
            )
            stored_data_id = (
                self.qwp_tile_generation_edition.cbx_stored_data.current_stored_data_id()
            )
            stored_data = manager.get_stored_data(
                datastore=datastore_id, stored_data=stored_data_id
            )
            fields = stored_data.get_fields()

            for field in fields:
                item = QListWidgetItem()
                item.setText(field)
                item.setFont(QtGui.QFont("Arial", 13))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.lwg_attribut.addItem(item)

        except StoredDataRequestManager.UnavailableStoredData as exc:
            msgBox = QMessageBox(
                QMessageBox.Warning,
                self.tr("Stored data read failed"),
                self.tr("Check details for more informations"),
            )
            msgBox.setDetailedText(str(exc))
            msgBox.exec()

    def get_selected_attributes(self) -> [str]:
        """
        Get list of selected attributes

        Returns:[str] selected attributes

        """
        attributes = []
        for i in range(0, self.lwg_attribut.count()):
            item = self.lwg_attribut.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                attributes.append(item.text())
        return attributes
