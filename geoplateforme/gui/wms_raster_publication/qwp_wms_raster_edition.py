# standard
import os

# PyQGIS
from qgis.PyQt import QtCore, uic
from qgis.PyQt.QtWidgets import QSlider, QWizardPage

# Plugin
from geoplateforme.gui.lne_validators import alphanum_qval


class WMSRasterEditionPageWizard(QWizardPage):
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

    def __init__(
        self,
        datastore_id: str,
        dataset_name: str,
        stored_data_id: str,
        parent=None,
    ):
        """
        QWizardPage to define tile parameters

        Args:
            parent: parent QObject
            datastore_id: datastore id
            dataset_name: dataset name
            stored_data_id: stored data id
        """

        super().__init__(parent)
        self.setTitle(self.tr("Publication WMS-Raster"))

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_wms_raster_edition.ui"),
            self,
        )

        self.datastore_id = datastore_id
        self.dataset_name = dataset_name
        self.stored_data_id = stored_data_id

        # To avoid some characters
        self.lne_flux.setValidator(alphanum_qval)

        # Define zoom levels range
        self.levels_range_slider.setMinimum(self.MIN_ZOOM_LEVEL)
        self.levels_range_slider.setMaximum(self.MAX_ZOOM_LEVEL)
        self.levels_range_slider.setLow(self.MIN_ZOOM_LEVEL)
        self.levels_range_slider.setHigh(self.MAX_ZOOM_LEVEL)
        self.levels_range_slider.setOrientation(QtCore.Qt.Horizontal)
        self.levels_range_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.levels_range_slider.setTickInterval(1)

        # Connect zoom level change to scale widget update
        self.levels_range_slider.sliderMoved.connect(self._levels_range_updated)
        self._levels_range_updated()
        self.srw_zoom.setEnabled(False)

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.lne_flux.setText("")

    def validatePage(self) -> bool:
        """
        Validate current page content

        Returns: True

        """
        valid = True
        return valid

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
