# standard

from qgis.PyQt.QtGui import QCloseEvent
from qgis.PyQt.QtWidgets import QWizard

# Plugin
from geoplateforme.gui.upload_database_integration.qwp_upload_database_integration import (
    UploadDatabaseIntegrationPageWizard,
)
from geoplateforme.gui.upload_database_integration.qwp_vector_db_edition import (
    VectorDbEditionPageWizard,
)


class UploadDatabaseIntegrationWizard(QWizard):
    def __init__(
        self,
        datastore_id: str,
        dataset_name: str,
        upload_id: str,
        upload_name: str,
        parent=None,
    ):
        """
        QWizard to for geoplateforme data import

        Args:
            parent: parent QObject
            datastore_id: datastored id
            dataset_name: dataset name
            upload_id : upload id
            upload_name: upload name
        """

        super().__init__(parent)
        self.setWindowTitle(
            self.tr("Intégration livraison en base de données vectorielle")
        )

        self.qwp_vector_db_edition = VectorDbEditionPageWizard(
            datastore_id=datastore_id,
            dataset_name=dataset_name,
            upload_id=upload_id,
            upload_name=upload_name,
            parent=self,
        )
        self.qwp_upload_database_integration = UploadDatabaseIntegrationPageWizard(
            qwp_vector_db_edition=self.qwp_vector_db_edition, parent=self
        )
        self.addPage(self.qwp_vector_db_edition)
        self.addPage(self.qwp_upload_database_integration)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)
        self.setOption(QWizard.WizardOption.NoCancelButtonOnLastPage, True)

    def reject(self) -> None:
        """Override reject to check last page and wait for database integration laucnh"""
        # If upload creation page, check that page is valid
        current_page = self.currentPage()
        if current_page == self.qwp_upload_database_integration:
            if current_page.validatePage():
                super().reject()
        else:
            super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Override closeEvent to check that current page is valid before close

        Args:
            event: QCloseEvent
        """
        # If upload creation page, check that page is valid
        current_page = self.currentPage()
        if current_page == self.qwp_upload_database_integration:
            if current_page.validatePage():
                event.accept()
            else:
                event.ignore()
        else:
            super().closeEvent(event)
