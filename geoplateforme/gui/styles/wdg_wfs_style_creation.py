# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QLabel, QWidget

# plugin
from geoplateforme.api.configuration import Configuration, ConfigurationType
from geoplateforme.gui.styles.wdg_sld_selection import SldSelectionWidget


class WfsStyleCreationWidget(QWidget):
    def __init__(self, parent: QWidget):
        """
        QWidget to define SLD path for each layer of a WFS configuration

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_wfs_style_creation.ui"), self
        )

        self._configuration = None
        self._layer_style_dict = {}

    def set_configuration(self, configuration: Configuration) -> None:
        """Define current configuration and add sld selection widget for each layer available in configuration

        :param configuration: configuration
        :type configuration: Configuration
        """
        if configuration.type != ConfigurationType.WFS:
            return
        used_data = configuration.type_infos["used_data"]
        for data in used_data:
            relations = data["relations"]
            for relation in relations:
                layer_name = f"{configuration.layer_name}:{relation['public_name']}"
                label = QLabel(layer_name)
                self.lyt_layer_config.addWidget(label)
                style_wdg = SldSelectionWidget()
                self.lyt_layer_config.addWidget(style_wdg)
                self._layer_style_dict[layer_name] = style_wdg

    def get_style_name(self) -> str:
        """Get style file path list for each available layers

        :return: style file path list
        :rtype: list[str]
        """
        return self.lne_name.text()

    def get_style_file_path(self) -> list[str]:
        """Get style file path list for each available layers

        :return: style file path list
        :rtype: list[str]
        """
        return list(self.get_layer_selected_sld().values())

    def get_layer_style_names(self) -> Optional[list[str]]:
        """Get layer style name list.

        :return: List of selected layer names
        :rtype: Optional[list[str]]
        """
        return list(self.get_layer_selected_sld().keys())

    def get_layer_selected_sld(self) -> dict[str, str]:
        """Return dict of selected sld path for each layer

        :return: dict of selected sld path for each layer
        :rtype: dict[str, str]
        """
        result = {}
        for layer_name, selection_widget in self._layer_style_dict.items():
            result[layer_name] = selection_widget.get_selected_stl_file()
        return result
