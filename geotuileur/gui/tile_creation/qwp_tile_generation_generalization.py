# standard
import os

# PyQGIS
from qgis.PyQt import QtCore, QtGui, uic
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import QLabel, QRadioButton, QWidget, QWizardPage

# Plugin
from geotuileur.__about__ import DIR_PLUGIN_ROOT
from geotuileur.gui.tile_creation.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)


class PixmapLabel(QLabel):
    def __init__(self, parent: QWidget = None):
        """
        QLabel implementation for QPixmap display and automatic pixmap rescale

        Args:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.setMinimumSize(1, 1)
        self.setScaledContents(False)
        self._pixmap = None

    def setPixmap(self, pm: QPixmap) -> None:
        self._pixmap = pm
        super().setPixmap(pm)

    def heightForWidth(self, width: int) -> int:
        if self._pixmap is None:
            return self.height()
        else:
            return int(self._pixmap.height() * width / self._pixmap.width())

    def sizeHint(self) -> QSize:
        w = self.width()
        return QSize(w, self.heightForWidth(w))

    def scaledPixmap(self) -> QPixmap:
        size = self.size()
        if (
            size.width() > self._pixmap.size().width()
            or size.height() > self._pixmap.size().height()
        ):
            size = self._pixmap.size()
        return self._pixmap.scaled(
            size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self._pixmap is not None:
            super().setPixmap(self.scaledPixmap())


class TileGenerationGeneralizationPageWizard(QWizardPage):
    def __init__(
        self, qwp_tile_generation_edition: TileGenerationEditionPageWizard, parent=None
    ):
        """
        QWizardPage to define fields for tile generation

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Select generalization option"))
        self.qwp_tile_generation_edition = qwp_tile_generation_edition

        uic.loadUi(
            os.path.join(
                os.path.dirname(__file__), "qwp_tile_generation_generalization.ui"
            ),
            self,
        )

        self.tippecanoe_options = {
            "simplify_forms": {
                "name": "simplify_forms",
                "title": self.tr("Simplification de données hétérogènes"),
                "explain": self.tr("Toutes les formes sont simplifiées."),
                "value": "-S10",
            },
            "keep_nodes": {
                "name": "keep_nodes",
                "title": self.tr("Simplification de réseau"),
                "explain": self.tr(
                    "Toutes les formes sont simplifiées et les nœuds du réseau sont conservés."
                ),
                "value": "-pn -S15",
            },
            "delete_smallest": {
                "name": "delete_smallest",
                "title": self.tr("Simplification de données linéaires autres"),
                "explain": self.tr("Les petits objets sont supprimés."),
                "value": "-an -S15",
            },
            "keep_cover": {
                "name": "keep_cover",
                "title": self.tr("Schématisation de données surfaciques"),
                "explain": self.tr(
                    "Les formes sont simplifiées en conservant une couverture du territoire."
                ),
                "value": "-aL -D8 -S15",
            },
            "keep_densest_delete_smallest": {
                "name": "keep_densest_delete_smallest",
                "title": self.tr("Sélection de données surfaciques"),
                "explain": self.tr(
                    "Les données les plus représentatives sont conservées et les "
                    "plus petites supprimées. Ce choix est pertinent si 3 attributs "
                    "ou moins sont conservés à l'étape précédente."
                ),
                "value": "-ac -aD -an -S15",
            },
            "merge_same_attributes_and_simplify": {
                "name": "merge_same_attributes_and_simplify",
                "title": self.tr("Fusion attributaire de données surfaciques"),
                "explain": self.tr(
                    "Les objets qui ont les mêmes valeurs d’attribut sont fusionnés tout en simplifiant "
                    "les formes et en supprimant les petites surfaces. "
                    "Ce choix est pertinent si 3 attributs ou moins sont conservés à l'étape précédente."
                ),
                "value": "-ac -an -S10",
            },
            "keep_shared_edges": {
                "name": "keep_shared_edges",
                "title": self.tr("Harmonisation de données surfaciques"),
                "explain": self.tr(
                    "Les formes sont simplifiées en conservant les limites partagées entre deux "
                    "surfaces."
                ),
                "value": "-ab -S20",
            },
        }

        self._add_tippecanoe_radiobuttons()

    def _add_tippecanoe_radiobuttons(self):
        nb_max_col = 2
        nb_row_for_options = 3
        minimum_width = 200
        i = 0
        for key, option in self.tippecanoe_options.items():
            # Define column from nb_max column
            column = i % nb_max_col

            # Define row from nb_max column
            row = i // nb_max_col * nb_row_for_options

            # Add radiobutton
            rb_option = QRadioButton(option["title"], self)
            rb_option.setMinimumWidth(minimum_width)
            self.tippecanoe_layout.addWidget(rb_option, row, column)
            row = row + 1

            # Store map of radiobutton
            option["radiobutton"] = rb_option

            # Add description label
            desc_label = QLabel(option["explain"], self)
            desc_label.setWordWrap(True)
            rb_option.setMinimumWidth(minimum_width)
            self.tippecanoe_layout.addWidget(desc_label, row, column)
            row = row + 1

            # Add PixmapLabel for example
            image_path = (
                DIR_PLUGIN_ROOT
                / "resources"
                / "images"
                / "tippecanoe"
                / f'{option["name"]}_merged.jpg'
            )

            pixmap = QPixmap(str(image_path))
            image_label = PixmapLabel(self)
            image_label.setMinimumWidth(minimum_width)
            image_label.setMinimumHeight(100)
            image_label.setPixmap(pixmap)
            self.tippecanoe_layout.addWidget(image_label, row, column)

            i = i + 1

    def get_tippecanoe_value(self) -> str:
        """
        Get selected generalization option tippecanoe value

        Returns: (str) selected tippecanoe value

        """
        for name, option in self.tippecanoe_options.items():
            if option["radiobutton"].isChecked():
                return option["value"]
