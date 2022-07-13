# standard

from qgis.PyQt.QtWidgets import QDialog, QWizard

from geotuileur.gui.publication_creation.qwp_publication_form import (
    PublicationFormPageWizard,
)
from geotuileur.gui.publication_creation.qwp_status import PublicationStatut

# Plugin


class PublicationFormCreation(QWizard):
    def __init__(self, parent=None):
        """
        QWizard to for geotuileur publication

        Args:
            parent: parent None
        """

        super().__init__(parent)
        self.setWindowTitle(self.tr("Publication creation"))
        self.qwp_publication_form = PublicationFormPageWizard(self)
        self.qwp_publication_status = PublicationStatut(self.qwp_publication_form, self)

        self.addPage(self.qwp_publication_form)
        self.addPage(self.qwp_publication_status)

        self.setOption(QWizard.NoCancelButtonOnLastPage, True)

    def accept(self) -> None:
        super().accept()
        if self.result() == QDialog.Accepted:
            self.restart()
