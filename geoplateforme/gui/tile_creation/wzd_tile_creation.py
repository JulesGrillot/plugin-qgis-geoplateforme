# standard

# PyQGIS
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
from geoplateforme.gui.tile_creation.qwp_tile_generation_sample import (
    TileGenerationSamplePageWizard,
)
from geoplateforme.gui.tile_creation.qwp_tile_generation_status import (
    TileGenerationStatusPageWizard,
)


class TileCreationWizard(QWizard):
    def __init__(self, parent=None):
        """
        QWizard to create tile vector in geotuileur platform

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setWindowTitle(self.tr("Tile creation"))

        self.qwp_tile_generation_edition = TileGenerationEditionPageWizard(self)
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
        self.qwp_tile_generation_sample = TileGenerationSamplePageWizard(
            self.qwp_tile_generation_edition, parent=self
        )
        self.qwp_tile_generation_status = TileGenerationStatusPageWizard(
            self.qwp_tile_generation_edition,
            self.qwp_tile_generation_fields_selection,
            self.qwp_tile_generation_generalization,
            self.qwp_tile_generation_sample,
            self,
        )
        self.addPage(self.qwp_tile_generation_edition)
        self.addPage(self.qwp_tile_generation_fields_selection)
        self.addPage(self.qwp_tile_generation_generalization)
        self.addPage(self.qwp_tile_generation_sample)
        self.addPage(self.qwp_tile_generation_status)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.NoBackButtonOnLastPage, True)
        self.setOption(QWizard.NoCancelButtonOnLastPage, True)

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.qwp_tile_generation_edition.set_datastore_id(datastore_id)

    def set_stored_data_id(self, stored_data_id: str) -> None:
        """
        Define current stored data from stored data id

        Args:
            stored_data_id: (str) stored data id
        """
        self.qwp_tile_generation_edition.set_stored_data_id(stored_data_id)
