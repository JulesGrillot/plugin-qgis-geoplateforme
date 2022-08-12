# standard
from qgis.PyQt.QtGui import QCloseEvent
from qgis.PyQt.QtWidgets import QWizard

# Plugin
from geotuileur.gui.update_tile_upload.qwp_update_tile_upload_edition import (
    UpdateTileUploadEditionPageWizard,
)
from geotuileur.gui.update_tile_upload.qwp_update_tile_upload_run import (
    UpdateTileUploadRunPageWizard,
)
from geotuileur.gui.upload_creation.qwp_upload_creation import UploadCreationPageWizard
from geotuileur.gui.upload_creation.qwp_upload_edition import UploadEditionPageWizard


class UpdateTileUploadWizard(QWizard):
    def __init__(self, parent=None):
        """
        QWizard to for geotuileur data import

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setWindowTitle(self.tr("Update tile upload"))

        self.qwp_update_tile_upload_edition = UpdateTileUploadEditionPageWizard(self)
        self.qwp_update_tile_upload_run = UpdateTileUploadRunPageWizard(
            qwp_upload_edition=self.qwp_update_tile_upload_edition, parent=self
        )
        self.addPage(self.qwp_update_tile_upload_edition)
        self.addPage(self.qwp_update_tile_upload_run)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.NoCancelButtonOnLastPage, True)

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.qwp_update_tile_upload_edition.set_datastore_id(datastore_id)

    def set_stored_data_id(self, stored_data_id: str) -> None:
        """
        Define current stored data from stored data id

        Args:
            stored_data_id: (str) stored data id
        """
        self.qwp_update_tile_upload_edition.set_stored_data_id(stored_data_id)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Override closeEvent to check that current page is valid before close

        Args:
            event: QCloseEvent
        """
        # If upload creation page, check that page is valid
        current_page = self.currentPage()
        if current_page == self.qwp_update_tile_upload_run:
            if current_page.validatePage():
                event.accept()
            else:
                event.ignore()
        else:
            super().closeEvent(event)
