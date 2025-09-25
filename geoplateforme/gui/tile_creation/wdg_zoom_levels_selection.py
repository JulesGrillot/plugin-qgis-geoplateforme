# standard
import os

# PyQGIS
from qgis.PyQt import QtCore, uic
from qgis.PyQt.QtWidgets import QSlider, QWidget

# Plugin


class ZoomLevelsSelectionWidget(QWidget):
    MIN_ZOOM_LEVEL = 5
    MAX_ZOOM_LEVEL = 18

    LEVEL_SCALE_LAMBERT_MAP = {
        5: 11700000,
        6: 5830000,
        7: 2900000,
        8: 1458000,
        9: 730000,
        10: 360000,
        11: 180000,
        12: 92000,
        13: 46000,
        14: 22800,
        15: 11400,
        16: 5700,
        17: 2800,
        18: 1400,
    }

    def __init__(self, parent: QWidget = None):
        """Widget to select zoom levels

        :param parent: parent widget, defaults to None
        :type parent: QWidget, optional
        """
        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_zoom_levels_selection.ui"),
            self,
        )

        # Define zoom levels range
        self.levels_range_slider.setMinimum(self.MIN_ZOOM_LEVEL)
        self.levels_range_slider.setMaximum(self.MAX_ZOOM_LEVEL)
        self.levels_range_slider.setLow(self.MIN_ZOOM_LEVEL)
        self.levels_range_slider.setHigh(self.MAX_ZOOM_LEVEL)
        self.levels_range_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.levels_range_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.levels_range_slider.setTickInterval(1)

        # Connect zoom level change to scale widget update
        self.levels_range_slider.sliderMoved.connect(self._levels_range_updated)
        self._levels_range_updated()
        self.srw_zoom.setEnabled(False)

    def set_table_name(self, table_name: str) -> None:
        """Define table name

        :param table_name: table name
        :type table_name: str
        """
        self.grp_table.setTitle(table_name)

    def get_bottom_level(self) -> int:
        """
        Get bottom level from range slider

        Returns: (int) bottom level

        """
        return self.levels_range_slider.high()

    def get_top_level(self) -> int:
        """
        Get top level from range slider

        Returns: (int) top level

        """
        return self.levels_range_slider.low()

    def _levels_range_updated(self) -> None:
        """
        Update zoom level widget when zoom level range is updated

        """
        self.srw_zoom.setScaleRange(
            self.LEVEL_SCALE_LAMBERT_MAP[self.levels_range_slider.low()],
            self.LEVEL_SCALE_LAMBERT_MAP[self.levels_range_slider.high()],
        )

        self.lbl_min_zoom.setText(str(self.levels_range_slider.low()))
        self.lbl_max_zoom.setText(str(self.levels_range_slider.high()))
