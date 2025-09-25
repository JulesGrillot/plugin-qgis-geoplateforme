# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage

# Plugin
from geoplateforme.gui.lne_validators import lower_case_num_qval


class TileGenerationEditionPageWizard(QWizardPage):
    def __init__(
        self,
        datastore_id: str,
        dataset_name: str,
        stored_data_id: str,
        parent=None,
    ):
        """
        QWizardPage to define tile parameters

        Args:
            parent: parent QObject
            datastore_id: datastore id
            dataset_name: dataset name
            stored_data_id: store data id
        """

        super().__init__(parent)

        self.datastore_id = datastore_id
        self.dataset_name = dataset_name
        self.stored_data_id = stored_data_id

        self.setTitle(self.tr("Define tile parameters"))

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_tile_generation_edition.ui"),
            self,
        )

        # To avoid some characters
        self.lne_name.setValidator(lower_case_num_qval)

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.lne_name.setText("")

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        valid = True

        if valid and len(self.lne_name.text()) == 0:
            valid = False
            QMessageBox.warning(
                self,
                self.tr("Missing informations."),
                self.tr("Please define tile name."),
            )

        return valid
