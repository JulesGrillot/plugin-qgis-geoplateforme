# standard
from PyQt5.QtWidgets import QWizard

# Plugin
from vectiler.gui.qwp_upload_creation import UploadCreationPageWizard
from vectiler.gui.qwp_upload_edition import UploadEditionPageWizard


class WzdImport(QWizard):
    def __init__(self, parent=None):
        """
        QWizard to for geotuileur data import

        Args:
            parent: parent QObject
        """

        super().__init__(parent)

        self.qwp_upload_edition = UploadEditionPageWizard(self)
        self.qwp_upload_creation = UploadCreationPageWizard(qwp_upload_edition=self.qwp_upload_edition, parent=self)
        self.addPage(self.qwp_upload_edition)
        self.addPage(self.qwp_upload_creation)
