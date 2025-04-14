# standard
import os

from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage
from qgis.utils import iface

from geoplateforme.gui.tile_creation.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)


class TileGenerationSamplePageWizard(QWizardPage):
    def __init__(
        self, qwp_tile_generation_edition: TileGenerationEditionPageWizard, parent=None
    ):
        """
        QWizardPage to define sample bbox use for tile generation

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Sample generation"))
        self.qwp_tile_generation_edition = qwp_tile_generation_edition

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_tile_generation_sample.ui"),
            self,
        )
        self.gpb_extent.setMapCanvas(iface.mapCanvas())
        # Extent always defined in WGS84
        self.gpb_extent.setOutputCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        self.chb_sample_generation.stateChanged.connect(self._sample_check_changed)
        self.setCommitPage(True)

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        pass

    def validatePage(self) -> bool:
        """
        Validate current page content by checking if extent is defined if sample asked

        Returns: True if sample parameters are valid, False otherwise

        """
        valid = True

        if self.is_sample_enabled():
            bbox = self.get_sample_box()
            valid = not bbox.isEmpty() and not bbox.isNull() and bbox.isFinite()
            if not valid:
                QMessageBox.warning(
                    self,
                    self.tr("No extent defined"),
                    self.tr("Please define extent for sample generation."),
                )

            if valid:
                stored_data = self.qwp_tile_generation_edition.cbx_stored_data.current_stored_data()
                vlayer = stored_data.create_extent_layer()
                extent = vlayer.extent()
                valid = extent.contains(bbox)
                if not valid:
                    QMessageBox.warning(
                        self,
                        self.tr("Invalid extent"),
                        self.tr(
                            "Invalid extent. Stored data extent is \n:"
                            " x_min {0} y_min {1} x_max {2} y_max {3}."
                        ).format(
                            extent.xMinimum(),
                            extent.yMinimum(),
                            extent.xMaximum(),
                            extent.yMaximum(),
                        ),
                    )

        return valid

    def _sample_check_changed(self) -> None:
        """
        Check sample enable to enable extent definition

        """
        self.gpb_extent.setEnabled(self.is_sample_enabled())

    def is_sample_enabled(self) -> bool:
        """
        Check if sample is enabled

        Returns: True if sample is enabled, False otherwise

        """
        return self.chb_sample_generation.isChecked()

    def get_sample_box(self) -> QgsRectangle:
        """
        Get sample box as a QgsRectangle

        Returns: (QgsRectangle) sample box

        """
        return self.gpb_extent.outputExtent()
