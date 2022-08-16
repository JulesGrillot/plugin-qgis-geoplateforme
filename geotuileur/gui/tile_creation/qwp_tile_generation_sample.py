# standard
import os

from qgis.core import QgsCoordinateReferenceSystem, QgsRectangle
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage
from qgis.utils import iface

from geotuileur.gui.tile_creation.qwp_tile_generation_edition import (
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
        self.chb_sample_generation.stateChanged.connect(self._sample_check_changed)
        self.setCommitPage(True)

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        stored_data = (
            self.qwp_tile_generation_edition.cbx_stored_data.current_stored_data()
        )
        srs = stored_data.srs
        self.gpb_extent.setOutputCrs(QgsCoordinateReferenceSystem(srs))

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
                stored_data = (
                    self.qwp_tile_generation_edition.cbx_stored_data.current_stored_data()
                )
                srs = stored_data.srs
                crs = QgsCoordinateReferenceSystem(srs)
                crs_bounds = crs.bounds()
                valid = crs_bounds.contains(bbox)
                if not valid:
                    QMessageBox.warning(
                        self,
                        self.tr("Invalid extent"),
                        self.tr(
                            "Invalid extent. Stored data projection bounds is \n:"
                            " x_min {0} y_min {1} x_max {2} y_max {3}."
                        ).format(
                            crs_bounds.xMinimum(),
                            crs_bounds.yMinimum(),
                            crs_bounds.xMaximum(),
                            crs_bounds.yMaximum(),
                        ),
                    )

            # TODO : add check of sample bbox size and bounds for stored data extent
            # => waiting for stored data extent geojson read

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
