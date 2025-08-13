# standard
from typing import Optional

# PyQGIS
from qgis.PyQt.QtWidgets import QWizard

# Plugin
from geoplateforme.gui.publication.qwp_visibility import VisibilityPageWizard
from geoplateforme.gui.qwp_metadata_form import MetadataFormPageWizard
from geoplateforme.gui.wmts_publication.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geoplateforme.gui.wmts_publication.qwp_wmts_publication_status import (
    PublicationStatut,
)


class WMTSPublicationWizard(QWizard):
    def __init__(
        self,
        parent=None,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
    ):
        """
        QWizard for WMTS-TMS publication

        Args:
            parent: parent None
            datastore_id: datastore id
            dataset_name: dataset name
            stored_data_id: store data id
        """

        super().__init__(parent)
        self.setWindowTitle(self.tr("Publication WMTS-TMS"))

        # First page to display publication form
        self.qwp_publication_form = PublicationFormPageWizard()

        # Third page to display metadata
        self.qwp_metadata_form = MetadataFormPageWizard(
            datastore_id, dataset_name, self
        )
        # Fourth page to define visibility
        self.qwp_visibility = VisibilityPageWizard(self)

        # Last page to launch processing and display results
        self.qwp_publication_status = PublicationStatut(
            self.qwp_publication_form,
            self.qwp_metadata_form,
            self.qwp_visibility,
            datastore_id,
            dataset_name,
            stored_data_id,
            self,
        )

        self.addPage(self.qwp_publication_form)
        self.addPage(self.qwp_metadata_form)
        self.addPage(self.qwp_visibility)
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

    def reject(self) -> None:
        """Override reject to check last page and wait for metadata publication"""
        # If service publication page, check that page is valid
        current_page = self.currentPage()
        if current_page == self.qwp_publication_status:
            if current_page.validatePage():
                super().reject()
        else:
            super().reject()
