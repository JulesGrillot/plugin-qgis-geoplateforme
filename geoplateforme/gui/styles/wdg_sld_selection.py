# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget


class SldSelectionWidget(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        """
        QWidget to select a sld file

        Args:
            parent: parent None

        """

        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_sld_selection.ui"),
            self,
        )

    def get_selected_stl_file(self) -> str:
        return self.wdg_stl_file.filePath()
