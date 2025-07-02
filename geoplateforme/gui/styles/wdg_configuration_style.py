# standard
import os

from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
)
from qgis.utils import OverrideCursor

# plugin
from geoplateforme.__about__ import DIR_PLUGIN_ROOT
from geoplateforme.api.configuration import Configuration
from geoplateforme.gui.styles.dlg_configuration_style_creation import (
    ConfigurationStyleCreationDialog,
)
from geoplateforme.processing.provider import GeoplateformeProvider
from geoplateforme.processing.style.delete_configuration_style import (
    DeleteConfigurationStyleAlgorithm,
)


class ConfigurationStylesWidget(QWidget):
    def __init__(self, parent: QWidget):
        """
        QWidget to display configuration style

        Args:
            parent:
        """
        super().__init__(parent)
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_configuration_style.ui"), self
        )

        self.btn_delete.setEnabled(False)
        self.btn_delete.setIcon(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/icons/Supprimer.svg"))
        )
        self.btn_delete.clicked.connect(self._delete_style)

        self.btn_add.setIcon(QIcon(":/images/themes/default/mActionAdd.svg"))
        self.btn_add.clicked.connect(self._add_style)

        # Table widget for styles
        self.tbw_styles.setColumnCount(1)
        self.tbw_styles.horizontalHeader().setVisible(False)
        self.tbw_styles.verticalHeader().setVisible(False)
        self.tbw_styles.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Connection for selection update
        self.tbw_styles.itemSelectionChanged.connect(
            self._update_style_delete_button_state
        )

        self._configuration = None

    def _update_style_delete_button_state(self) -> None:
        """Enable delete button if at least one row is selected for style table."""
        selected_rows = {item.row() for item in self.tbw_styles.selectedItems()}
        self.btn_delete.setEnabled(bool(selected_rows))

    def set_configuration(self, configuration: Configuration) -> None:
        """Define current configuration

        :param configuration: configuration
        :type configuration: Configuration
        """
        self._configuration = configuration

        # Clear table
        self.tbw_styles.setRowCount(0)

        # Check if extra is defined to get styles
        extra = configuration.extra
        if extra is None:
            return

        if config_style := extra.get("styles", None):
            # Add each style
            for style in config_style:
                row = self.tbw_styles.rowCount()
                self.tbw_styles.insertRow(row)
                item = QTableWidgetItem(style["name"])
                self.tbw_styles.setItem(row, 0, item)

    def _delete_style(self) -> None:
        """Remove selected styles"""
        rows = [x.row() for x in self.tbw_styles.selectedIndexes()]
        rows.sort(reverse=True)
        for row in rows:
            item = self.tbw_styles.item(row, 0)
            if self._delete_configuration_style(item.text()):
                self.tbw_styles.removeRow(row)

    def _delete_configuration_style(self, style_name: str) -> bool:
        """Delete a configuration style with associated processing

        :param style_name: style name to delete
        :type style_name: str
        :return: True if style was removed from config, False if an error occured
        :rtype: bool
        """
        algo_str = f"{GeoplateformeProvider().id()}:{DeleteConfigurationStyleAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        params = {
            DeleteConfigurationStyleAlgorithm.DATASTORE_ID: self._configuration.datastore_id,
            DeleteConfigurationStyleAlgorithm.CONFIGURATION_ID: self._configuration._id,
            DeleteConfigurationStyleAlgorithm.STYLE_NAME: style_name,
        }
        _, success = alg.run(params, context, feedback)

        if not success:
            QMessageBox.warning(
                self,
                self.tr("Erreur lors de la suppression du style."),
                feedback.textLog(),
            )
            return False
        return True

    def _add_style(self) -> None:
        """Display dialog to create a configuration style"""
        with OverrideCursor(Qt.CursorShape.WaitCursor):
            dialog = ConfigurationStyleCreationDialog(
                configuration=self._configuration, parent=self
            )
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self._configuration.update_from_api()
            self.set_configuration(self._configuration)
