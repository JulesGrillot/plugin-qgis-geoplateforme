# standard
from typing import Optional

# PyQGIS
from qgis.PyQt.QtWidgets import QWizard

# Plugin
from geoplateforme.gui.wms_raster_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.gui.wms_raster_publication.qwp_wms_raster_edition import (
    WMSRasterEditionPageWizard,
)
from geoplateforme.gui.wms_raster_publication.qwp_wms_raster_publication_status import (
    PublicationStatut,
)


class WMSRasterPublicationWizard(QWizard):
    def __init__(
        self,
        parent=None,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
    ):
        """
        QWizard for WMS-RASTER publication

        Args:
            parent: parent None
            datastore_id: datastore id
            dataset_name: dataset name
            stored_data_id: store data id
        """

        super().__init__(parent)
        self.setWindowTitle(self.tr("Publication WMS-Raster"))

        # First page to define stored data and table relation
        self.qwp_wms_raster_edition = WMSRasterEditionPageWizard(
            datastore_id=datastore_id,
            dataset_name=dataset_name,
            stored_data_id=stored_data_id,
            parent=self,
        )

        # Second page to display publication form
        self.qwp_publication_form = PublicationFormPageWizard()

        # Last page to launch processing and display results
        self.qwp_publication_status = PublicationStatut(
            self.qwp_wms_raster_edition, self.qwp_publication_form, self
        )

        self.addPage(self.qwp_wms_raster_edition)
        self.addPage(self.qwp_publication_form)
        self.addPage(self.qwp_publication_status)

        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)
        self.setOption(QWizard.WizardOption.NoCancelButtonOnLastPage, True)

    def get_offering_id(self) -> str:
        """Get offering id of created service

        :return: offering id
        :rtype: str
        """
        return self.qwp_publication_status.offering_id
