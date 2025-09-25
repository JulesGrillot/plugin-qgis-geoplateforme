# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage
from qgis.utils import OverrideCursor

# Plugin
from geoplateforme.api.stored_data import (
    StoredDataStatus,
    StoredDataStep,
    StoredDataType,
)
from geoplateforme.gui.lne_validators import lower_case_num_qval


class TileGenerationEditionPageWizard(QWizardPage):
    def __init__(
        self,
        parent=None,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
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
        self.setTitle(self.tr("Define tile parameters"))

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_tile_generation_edition.ui"),
            self,
        )

        # Only display stored data ready for pyramid generation
        self.cbx_stored_data.set_filter_type([StoredDataType.VECTORDB])
        self.cbx_stored_data.set_visible_steps(
            [StoredDataStep.TILE_CREATED, StoredDataStep.TILE_GENERATION]
        )
        self.cbx_stored_data.set_visible_status([StoredDataStatus.GENERATED])

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self.cbx_dataset.currentIndexChanged.connect(self._dataset_updated)
        self.cbx_stored_data.currentIndexChanged.connect(self._stored_data_updated)

        # To avoid some characters
        self.lne_name.setValidator(lower_case_num_qval)

        if datastore_id:
            self.set_datastore_id(datastore_id)
            self.cbx_datastore.setEnabled(False)
        self._datastore_updated()

        if dataset_name:
            self.set_dataset_name(dataset_name)
            self.cbx_dataset.setEnabled(False)
        self._dataset_updated()

        if stored_data_id:
            self.set_stored_data_id(stored_data_id)
            self.cbx_stored_data.setEnabled(False)
        self._stored_data_updated()

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

        if not self.cbx_datastore.current_datastore_id():
            valid = False
            QMessageBox.warning(
                self,
                self.tr("No datastore selected."),
                self.tr("Please select a datastore"),
            )

        if valid and not self.cbx_stored_data.current_stored_data_id():
            valid = False
            QMessageBox.warning(
                self,
                self.tr("No stored data selected."),
                self.tr("Please select a stored data"),
            )

        if valid and len(self.lne_name.text()) == 0:
            valid = False
            QMessageBox.warning(
                self,
                self.tr("Missing informations."),
                self.tr("Please define tile name."),
            )

        return valid

    def _datastore_updated(self) -> None:
        """
        Update stored data combobox when datastore is updated

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
            self.cbx_stored_data.currentIndexChanged.disconnect(
                self._stored_data_updated
            )
            self.cbx_stored_data.set_datastore(
                self.cbx_datastore.current_datastore_id(),
                self.cbx_dataset.current_dataset_name(),
            )
            self.cbx_stored_data.currentIndexChanged.connect(self._stored_data_updated)
            self._stored_data_updated()

    def _stored_data_updated(self) -> None:
        """
        Define default flux name from stored data

        """
        if self.cbx_stored_data.current_stored_data_name():
            self.lne_name.setText(self.cbx_stored_data.current_stored_data_name())
