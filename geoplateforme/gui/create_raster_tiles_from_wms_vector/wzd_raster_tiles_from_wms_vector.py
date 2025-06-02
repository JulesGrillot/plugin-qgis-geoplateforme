# standard

# PyQGIS

from qgis.PyQt.QtWidgets import QWizard

from geoplateforme.gui.create_raster_tiles_from_wms_vector.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)
from geoplateforme.gui.create_raster_tiles_from_wms_vector.qwp_tile_generation_status import (
    TileGenerationStatusPageWizard,
)


class TileRasterCreationWizard(QWizard):
    def __init__(
        self,
        datastore_id: str,
        dataset_name: str,
        offering_id: str,
        parent=None,
    ):
        """
        QWizard to create tile vector in geoplateforme platform

        Args:
            parent: parent QObject
            datastore_id: datastore id
            dataset_name: dataset name
            offering_id: offering id
        """

        super().__init__(parent)
        self.setWindowTitle(self.tr("Génération des tuiles raster"))

        self.qwp_tile_generation_edition = TileGenerationEditionPageWizard(
            datastore_id,
            dataset_name,
            offering_id,
            self,
        )
        self.qwp_tile_generation_status = TileGenerationStatusPageWizard(
            self.qwp_tile_generation_edition,
            self,
        )
        self.addPage(self.qwp_tile_generation_edition)
        self.addPage(self.qwp_tile_generation_status)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)
        self.setOption(QWizard.WizardOption.NoCancelButtonOnLastPage, True)

    def get_created_stored_data_id(self) -> str:
        """Return created stored data id

        :return: created stored data id
        :rtype: str
        """
        return self.qwp_tile_generation_status.created_stored_data_id
