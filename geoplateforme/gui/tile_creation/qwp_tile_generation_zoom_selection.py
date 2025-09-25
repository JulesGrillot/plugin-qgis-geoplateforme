# standard
import os
from typing import Dict, Tuple

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QWizardPage
from qgis.utils import OverrideCursor

# Project
from geoplateforme.gui.tile_creation.qwp_tile_generation_fields_selection import (
    TileGenerationFieldsSelectionPageWizard,
)
from geoplateforme.gui.tile_creation.wdg_zoom_levels_selection import (
    ZoomLevelsSelectionWidget,
)


class TileGenerationZoomSelectionPageWizard(QWizardPage):
    def __init__(
        self,
        qwp_tile_generation_fields_selection: TileGenerationFieldsSelectionPageWizard,
        parent=None,
    ):
        """
        QWizardPage to define zoom levels for tile generation

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Select zoom levels for tables"))
        self.qwp_tile_generation_fields_selection = qwp_tile_generation_fields_selection

        uic.loadUi(
            os.path.join(
                os.path.dirname(__file__), "qwp_tile_generation_zoom_selection.ui"
            ),
            self,
        )

        self.table_zoom_widgets = {}

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        with OverrideCursor(Qt.CursorShape.WaitCursor):
            for _, widget in self.table_zoom_widgets.items():
                widget.setVisible(False)

            selected_attributes = (
                self.qwp_tile_generation_fields_selection.get_selected_attributes()
            )
            for table_name, _ in selected_attributes.items():
                if table_name not in self.table_zoom_widgets:
                    wdg_table_zoom_levels = ZoomLevelsSelectionWidget(self)
                    wdg_table_zoom_levels.set_table_name(table_name)
                    self.table_zoom_widgets[table_name] = wdg_table_zoom_levels
                else:
                    wdg_table_zoom_levels = self.table_zoom_widgets[table_name]
                    wdg_table_zoom_levels.setVisible(True)
                self.lyt_table_zoom_level.addWidget(wdg_table_zoom_levels)

    def get_selected_zoom_levels(self) -> Dict[str, Tuple[int, int]]:
        """
        Get selected zoom levels

        Returns: {str:Tuple[int,int]} map of selected zoom levels (bottom,top) for each table

        """
        selected_zooms_levels = {}
        selected_attributes = (
            self.qwp_tile_generation_fields_selection.get_selected_attributes()
        )
        for table_name, _ in selected_attributes.items():
            wdg_table_zoom_levels = self.table_zoom_widgets[table_name]
            selected_zooms_levels[table_name] = (
                wdg_table_zoom_levels.get_bottom_level(),
                wdg_table_zoom_levels.get_top_level(),
            )
        return selected_zooms_levels

    def validatePage(self) -> bool:
        """
        Validate current page content by zoom levels

        Returns: True

        """
        valid = True
        return valid
