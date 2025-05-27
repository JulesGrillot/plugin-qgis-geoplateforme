# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage


class VectorDbEditionPageWizard(QWizardPage):
    def __init__(
        self,
        datastore_id: str,
        dataset_name: str,
        upload_id: str,
        upload_name: str,
        parent=None,
    ):
        """
        QWizardPage to define current geoplateforme import data

        Args:
            parent: parent QObject
            datastore_id: datastored id
            dataset_name: dataset name
            upload_id : upload id
        """

        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_vector_db_edition.ui"), self
        )

        self.datastore_id = datastore_id
        self.dataset_name = dataset_name
        self.upload_id = upload_id
        self.lne_name.setText(upload_name)

        self.setCommitPage(True)

    def get_name(self) -> str:
        return self.lne_name.text()

    def validatePage(self) -> bool:
        """
        Validate current page content by checking name

        Returns: True

        """

        return self.lne_name.text() != ""
