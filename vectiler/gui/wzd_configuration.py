# standard

# PyQGIS
from qgis.PyQt.QtWidgets import  QWizard

from vectiler.gui.qwp_tile_generation_edition import TileGenerationEditionPageWizard
from vectiler.gui.qwp_tile_generation_fields_selection import TileGenerationFieldsSelectionPageWizard
from vectiler.gui.qwp_tile_generation_generalization import TileGenerationGeneralizationPageWizard


class WzdConfiguration(QWizard):
    def __init__(self, parent=None):
        """
        Dialog to define current geotuileur configuration data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)

        self.qwp_tile_generation_edition = TileGenerationEditionPageWizard(self)
        self.qwp_tile_generation_fields_selection = TileGenerationFieldsSelectionPageWizard(self.qwp_tile_generation_edition, self)
        self.qwp_tile_generation_generalization = TileGenerationGeneralizationPageWizard(self.qwp_tile_generation_edition, parent=self)
        self.addPage(self.qwp_tile_generation_edition)
        self.addPage(self.qwp_tile_generation_fields_selection)
        self.addPage(self.qwp_tile_generation_generalization)
