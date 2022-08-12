# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage


class UploadEditionPageWizard(QWizardPage):
    def __init__(self, parent=None):

        """
        QWizardPage to define current geotuileur import data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Upload data"))

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_upload_edition.ui"), self
        )

        self.setCommitPage(True)

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.cbx_datastore.set_datastore_id(datastore_id)

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """

        return self.wdg_upload_creation.validateWidget()
