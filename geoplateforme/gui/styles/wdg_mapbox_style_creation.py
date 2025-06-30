# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget


class MapboxStyleCreationWidget(QWidget):
    def __init__(self, parent: QWidget):
        """
        QWidget to style from mapbox .json

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_mapbox_style_creation.ui"),
            self,
        )

    def get_selected_mapbox_file(self) -> str:
        """Return selected mapbox file

        :return: _description_
        :rtype: str
        """
        return self.wdg_mapbox_file.filePath()

    def get_style_file_path(self) -> list[str]:
        """Get style file path list for each available layers

        :return: style file path list
        :rtype: list[str]
        """
        return [self.get_selected_mapbox_file()]

    def get_layer_style_names(self) -> Optional[list[str]]:
        """Get layer style name list.
        This is a configuration for mapbox, there is no layer style name.
        We always return None

        :return: None
        :rtype: Optional[list[str]]
        """
        return None

    def get_style_name(self) -> str:
        """Get name of style

        :return: style name
        :rtype: str
        """
        return self.lne_name.text()
