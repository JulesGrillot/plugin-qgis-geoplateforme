# standard
import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWizardPage, QSlider, QMessageBox
from qgis.PyQt import uic


class TileGenerationEditionPageWizard(QWizardPage):
    STORED_DATA_ID_FIELD = "stored_data_id"

    MIN_ZOOM_LEVEL = 5
    MAX_ZOOM_LEVEL = 18

    LEVEL_SCALE_LAMBERT_MAP = {5: 11666284,
                               6: 5833093,
                               7: 2916534,
                               8: 1458263,
                               9: 729131,
                               10: 364565,
                               11: 182283,
                               12: 91141,
                               13: 45570,
                               14: 22785,
                               15: 11393,
                               16: 5696,
                               17: 2848,
                               18: 1424
                               }

    def __init__(self, parent=None):
        """
        QWizardPage to define tile parameters

        Args:
            parent: parent QObject
        """

        super().__init__(parent)

        uic.loadUi(os.path.join(os.path.dirname(__file__), "qwp_tile_generation_edition.ui"), self)

        # Only display stored data ready for pyramid generation
        self.cbx_stored_data.set_filter_type(["VECTOR-DB"])
        self.cbx_stored_data.set_expected_tags(["upload_id", "proc_int_id"])
        self.cbx_stored_data.set_forbidden_tags(["pyramid_id"])

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self._datastore_updated()

        self.cbx_stored_data.currentIndexChanged.connect(self._stored_data_updated)
        self._stored_data_updated()

        # To avoid some characters
        rx = QtCore.QRegExp("[a-z-A-Z-0-9-_]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lne_flux.setValidator(validator)

        # Define zoom levels range
        self.levels_range_slider.setMinimum(self.MIN_ZOOM_LEVEL)
        self.levels_range_slider.setMaximum(self.MAX_ZOOM_LEVEL)
        self.levels_range_slider.setLow(self.MIN_ZOOM_LEVEL)
        self.levels_range_slider.setHigh(self.MAX_ZOOM_LEVEL)
        self.levels_range_slider.setOrientation(QtCore.Qt.Horizontal)
        self.levels_range_slider.setTickPosition(QSlider.TicksBelow)
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
        self._datastore_updated()
        self._stored_data_updated()

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        valid = True

        if not self.cbx_datastore.current_datastore_id():
            valid = False
            QMessageBox.warning(self, self.tr("No datastore selected."), self.tr("Please select a datastore"))

        if valid and not self.cbx_stored_data.current_stored_data_id():
            valid = False
            QMessageBox.warning(self, self.tr("No stored data selected."), self.tr("Please select a stored data"))

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

    def _datastore_updated(self) -> None:
        """
        Update stored data combobox when datastore is updated

        """
        self.cbx_stored_data.set_datastore(self.cbx_datastore.current_datastore_id())

    def _stored_data_updated(self) -> None:
        """
        Define default flux name from stored data

        """
        if self.cbx_stored_data.current_stored_data_name() and not self.lne_flux.text():
            self.lne_flux.setText(self.cbx_stored_data.current_stored_data_name())

    def _levels_range_updated(self) -> None:
        """
        Update zoom level widget when zoom level range is updated

        """
        self.srw_zoom.setScaleRange(self.LEVEL_SCALE_LAMBERT_MAP[self.levels_range_slider.low()],
                                    self.LEVEL_SCALE_LAMBERT_MAP[self.levels_range_slider.high()])
