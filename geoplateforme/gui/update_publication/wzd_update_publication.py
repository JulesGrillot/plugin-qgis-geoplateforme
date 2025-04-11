# standard

from qgis.PyQt.QtWidgets import QDialog, QWizard

# Plugin
from geoplateforme.gui.update_publication.qwp_update_publication_form import (
    UpdatePublicationPageWizard,
)
from geoplateforme.gui.update_publication.qwp_update_status import (
    UpdatePublicationStatusPageWizard,
)


class UpdatePublicationWizard(QWizard):
    def __init__(self, parent=None):
        """
        QWizard for update a publication

        Args:
            parent: parent None
        """

        super().__init__(parent)
        self.setWindowTitle(self.tr("Publication update"))
        self.qwp_update_publication_form = UpdatePublicationPageWizard(self)
        self.qwp_update_publication_status = UpdatePublicationStatusPageWizard(
            self.qwp_update_publication_form, self
        )

        self.addPage(self.qwp_update_publication_form)
        self.addPage(self.qwp_update_publication_status)

        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.NoCancelButtonOnLastPage, True)

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.qwp_update_publication_form.set_datastore_id(datastore_id)

    def set_stored_data_id(self, stored_data_id: str) -> None:
        """
        Define current stored data from stored data id

        Args:
            stored_data_id: (str) stored data id
        """
        self.qwp_update_publication_form.set_stored_data_id(stored_data_id)

    def accept(self) -> None:
        super().accept()
        if self.result() == QDialog.Accepted:
            self.restart()
