# standard

# PyQGIS
from qgis.PyQt.QtWidgets import QDialog, QWizard

from geotuileur.gui.tile_creation.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)
from geotuileur.gui.tile_creation.qwp_tile_generation_fields_selection import (
    TileGenerationFieldsSelectionPageWizard,
)
from geotuileur.gui.tile_creation.qwp_tile_generation_generalization import (
    TileGenerationGeneralizationPageWizard,
)
from geotuileur.gui.tile_creation.qwp_tile_generation_status import (
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
        self.setOption(QWizard.NoCancelButtonOnLastPage, True)
