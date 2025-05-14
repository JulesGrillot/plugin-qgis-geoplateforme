# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QWizardPage
from qgis.utils import OverrideCursor

from geoplateforme.api.stored_data import StoredDataStatus, StoredDataType


class PublicationFormPageWizard(QWizardPage):
    def __init__(self, parent=None):
        """
        QWizardPage to define current geoplateforme publication

        Args:None

        """

        super().__init__(parent)
        self.setTitle(self.tr("Describe and publish your tiles"))

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_publication_form.ui"), self
        )

        # Only display pyramid generation ready for publication
        self.cbx_stored_data.set_filter_type([StoredDataType.PYRAMIDVECTOR])
        self.cbx_stored_data.set_visible_status([StoredDataStatus.GENERATED])

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self.cbx_dataset.currentIndexChanged.connect(self._dataset_updated)

        self._datastore_updated()

        self.setCommitPage(True)

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.cbx_datastore.set_datastore_id(datastore_id)

    def set_dataset_name(self, dataset_name: str) -> None:
        """
        Define current dataset name

        Args:
            dataset_name: (str) dataset name
        """
        self.cbx_dataset.set_dataset_name(dataset_name)

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

        return self.wdg_publication_form.validatePage()

    def _datastore_updated(self) -> None:
        """
        Update dataset combobox when datastore is updated

        """
        with OverrideCursor(Qt.CursorShape.WaitCursor):
            self.cbx_dataset.currentIndexChanged.disconnect(self._dataset_updated)
            self.cbx_dataset.set_datastore_id(self.cbx_datastore.current_datastore_id())
            self.cbx_dataset.currentIndexChanged.connect(self._dataset_updated)
            self._dataset_updated()

    def _dataset_updated(self) -> None:
        """
        Update stored data combobox when dataset is updated

        """
        with OverrideCursor(Qt.CursorShape.WaitCursor):
            self.cbx_stored_data.set_datastore(
                self.cbx_datastore.current_datastore_id(),
                self.cbx_dataset.current_dataset_name(),
            )
