# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage


class VisibilityPageWizard(QWizardPage):
    def __init__(
        self,
        parent=None,
    ):
        """
        QWizardPage to define publication visibility

        Args:
            parent: parent None
        """

        super().__init__(parent)
        self.setTitle(self.tr("Restrictions d'accès"))

        uic.loadUi(os.path.join(os.path.dirname(__file__), "qwp_visibility.ui"), self)

    def is_open(self) -> bool:
        """Define if publication is open

        :return: True if publication is open, False otherwise
        :rtype: bool
        """
        return self.rbtn_open.isChecked()

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        return True
