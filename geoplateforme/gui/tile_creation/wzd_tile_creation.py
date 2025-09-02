# standard

# PyQGIS
from typing import Optional

from qgis.PyQt.QtWidgets import QWizard

from geoplateforme.gui.tile_creation.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)
from geoplateforme.gui.tile_creation.qwp_tile_generation_fields_selection import (
    TileGenerationFieldsSelectionPageWizard,
)
from geoplateforme.gui.tile_creation.qwp_tile_generation_generalization import (
    TileGenerationGeneralizationPageWizard,
)
from geoplateforme.gui.tile_creation.qwp_tile_generation_status import (
    TileGenerationStatusPageWizard,
)


class TileCreationWizard(QWizard):
    def __init__(
        self,
        parent=None,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
    ):
        """
        QWizard to create tile vector in geoplateforme platform

        Args:
            parent: parent QObject
            datastore_id: datastore id
            dataset_name: dataset name
            stored_data_id: store data id
        """

        super().__init__(parent)
        self.setWindowTitle(self.tr("Tile creation"))

        self.qwp_tile_generation_edition = TileGenerationEditionPageWizard(
            self, datastore_id, dataset_name, stored_data_id
        )
        self.qwp_tile_generation_fields_selection = (
            TileGenerationFieldsSelectionPageWizard(
                self.qwp_tile_generation_edition, self
            )
        )
        self.qwp_tile_generation_generalization = (
            TileGenerationGeneralizationPageWizard(
                self.qwp_tile_generation_edition, parent=self
            )
        )
        self.qwp_tile_generation_status = TileGenerationStatusPageWizard(
            self.qwp_tile_generation_edition,
            self.qwp_tile_generation_fields_selection,
            self.qwp_tile_generation_generalization,
            self,
        )
        self.addPage(self.qwp_tile_generation_edition)
        self.addPage(self.qwp_tile_generation_fields_selection)
        self.addPage(self.qwp_tile_generation_generalization)
        self.addPage(self.qwp_tile_generation_status)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)
        self.setOption(QWizard.WizardOption.NoCancelButtonOnLastPage, True)

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.qwp_tile_generation_edition.set_datastore_id(datastore_id)

    def set_dataset_name(self, dataset_name: str) -> None:
        """
        Define current dataset name

        Args:
            dataset_name: (str) dataset name
        """
        self.qwp_tile_generation_edition.set_dataset_name(dataset_name)

    def set_stored_data_id(self, stored_data_id: str) -> None:
        """
        Define current stored data from stored data id

        Args:
            stored_data_id: (str) stored data id
        """
        self.qwp_tile_generation_edition.set_stored_data_id(stored_data_id)

    def get_created_stored_data_id(self) -> str:
        """Return created stored data id

        :return: created stored data id
        :rtype: str
        """
        return self.qwp_tile_generation_status.created_stored_data_id
