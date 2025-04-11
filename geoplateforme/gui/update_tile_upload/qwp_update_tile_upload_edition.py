# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage

# Plugin
from geoplateforme.api.stored_data import StoredDataStep


class UpdateTileUploadEditionPageWizard(QWizardPage):
    def __init__(self, parent=None):
        """
        QWizardPage to define current geoplateforme import data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Update tile upload data"))

        uic.loadUi(
            os.path.join(
                os.path.dirname(__file__), "qwp_update_tile_upload_edition.ui"
            ),
            self,
        )
        # Only display published stored data
        self.cbx_stored_data.set_visible_steps([StoredDataStep.PUBLISHED])

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self._datastore_updated()

        self.cbx_stored_data.currentIndexChanged.connect(self._stored_data_updated)
        self._stored_data_updated()

        self.setCommitPage(True)

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.cbx_datastore.set_datastore_id(datastore_id)

    def set_stored_data_id(self, stored_data_id: str) -> None:
        """
        Define current stored data from stored data id

        Args:
            stored_data_id: (str) stored data id
        """
        self.cbx_stored_data.set_stored_data_id(stored_data_id)

    def _datastore_updated(self) -> None:
        """
        Update stored data combobox when datastore is updated

        """
        self.cbx_stored_data.set_datastore(self.cbx_datastore.current_datastore_id())

    def _stored_data_updated(self) -> None:
        """
        Define default flux name from stored data

        """
        if self.cbx_stored_data.current_stored_data_name():
            self.wdg_upload_creation.set_name(
                f"{self.cbx_stored_data.current_stored_data_name()} maj"
            )

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        valid = self.wdg_upload_creation.validateWidget()

        if valid and not self.cbx_stored_data.current_stored_data_id():
            valid = False
            QMessageBox.warning(
                self,
                self.tr("No stored data defined."),
                self.tr("Please define stored data"),
            )

        return valid
