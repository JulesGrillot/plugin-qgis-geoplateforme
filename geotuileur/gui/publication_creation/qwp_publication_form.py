# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage

from geotuileur.api.stored_data import StoredDataStatus, StoredDataStep


class PublicationFormPageWizard(QWizardPage):
    def __init__(self, parent=None):

        """
        QWizardPage to define current geotuileur publication

        Args:None

        """

        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_publication_form.ui"), self
        )

        # Only display pyramid generation ready for publication
        self.cbx_stored_data.set_filter_type(["ROK4-PYRAMID-VECTOR"])
        self.cbx_stored_data.set_visible_steps([StoredDataStep.TILE_PUBLICATION])
        self.cbx_stored_data.set_visible_status([StoredDataStatus.GENERATED])

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)

        self._datastore_updated()

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

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        if (
            len(self.wdg_publication_form.lne_name.text()) == 0
            or len(self.wdg_publication_form.lne_title.text()) == 0
            or len(self.wdg_publication_form.txe_abstract.toPlainText()) == 0
            or len(self.wdg_publication_form.lne_legal_notice.text()) == 0
            or len(self.wdg_publication_form.lne_url_legal.text()) == 0
        ):
            valid = False
            QMessageBox.warning(
                self,
                self.tr("Missing informations."),
                self.tr("Please fill all fields."),
            )
        else:
            valid = True

        return valid

    def _datastore_updated(self) -> None:
        """
        Update pyramid generation combobox when datastore is updated

        """

        self.cbx_stored_data.set_datastore(self.cbx_datastore.current_datastore_id())
